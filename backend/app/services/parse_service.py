"""???????????

BackgroundTasks ???????????
???? + ?? ? DeepSeek ??? ? ???? ? ??
"""
import json
import re as _re_module
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.normalize import skill_matcher
from app.core.parsing import extractor
from app.db.session import AsyncSessionLocal
from app.infrastructure.llm.deepseek_client import deepseek_client
from app.infrastructure.storage.file_store import file_store
from app.models.entities.skill import Skill
from app.models.entities.user_skill import UserSkill
from app.models.enums.status import SkillStatusEnum
from app.repositories import (
    parse_task_repository,
    resume_repository,
    skill_repository,
    skill_synonym_repository,
    user_skill_repository,
)
from app.repositories import (
    user_profile_repository as _user_profile_repository,
    user_work_experience_repository as _user_work_experience_repository,
)


async def run_parse_pipeline(file_id: int, user_id: int) -> None:
    """??????????

    ? BackgroundTasks ??????????? AsyncSession?

    Args:
        file_id: upload_file ???
        user_id: ?????
    """
    async with AsyncSessionLocal() as db:
        try:
            # 1. ?? parse_task ? PARSING
            task = await parse_task_repository.get_by_file_and_user(db, file_id, user_id)
            if task is None:
                return
            task.status = "PARSING"
            await parse_task_repository.update(db, task)
            await db.commit()

            # 2. ??????
            from app.repositories import upload_file_repository
            upload_entity = await upload_file_repository.get_by_id(db, file_id)
            if upload_entity is None:
                raise ValueError("upload_file ?????")

            # 3. ??????
            disk_path = file_store.resolve_path(upload_entity.path)
            raw_text = extractor.extract_text(str(disk_path))

            # 4. ?????? PDF?
            images = extractor.extract_images_as_base64(str(disk_path))

            # 5. ?? DeepSeek ?????
            structured = await _extract_structured(db, raw_text, images)

            # 5a. Normalize DeepSeek field names for frontend
            #     workYears -> years, education object -> string, skills -> flat names
            if "years" not in structured and "workYears" in structured:
                structured["years"] = structured["workYears"]
            if isinstance(structured.get("education"), dict):
                edu_obj = structured["education"]
                structured["education"] = edu_obj.get("degree") or edu_obj.get("name") or ""
            import re as _re2
            if isinstance(structured.get("skills"), list):
                flat = []
                for s in structured["skills"]:
                    if isinstance(s, str):
                        # Strip parenthetical annotations like "Java?????Spring Boot?..."
                        name_part = s.split("：")[0].split(":")[0].strip()
                        # Remove (xxx) or?xxx?parenthetical
                        name_clean = _re2.sub(r"[（(].*?[）)]", "", name_part).strip()
                        if name_clean and len(name_clean) < 40:
                            flat.append(name_clean)
                        # Extract sub-skills after colon
                        if "：" in s or ":" in s:
                            rest = s.split("：", 1)[-1].split(":", 1)[-1]
                            for sub in _re2.split(r"[,，、；;]", rest):
                                sub = sub.strip()
                                # Strip parenthetical from sub-skills too
                                sub = _re2.sub(r"[（(].*?[）)]", "", sub).strip()
                                if sub and len(sub) < 40:
                                    flat.append(sub)
                    elif isinstance(s, dict):
                        name = s.get("name") or s.get("category") or ""
                        if name and len(name) < 40:
                            flat.append(name)
                        if s.get("details"):
                            for d in s["details"]:
                                if isinstance(d, str) and d.strip():
                                    flat.append(d.strip())
                # Deduplicate while preserving order
                seen = set()
                deduped = []
                for name in flat:
                    name = name.strip()
                    if name and name not in seen:
                        seen.add(name)
                        deduped.append(name)
                structured["skills"] = deduped


            # 6. ????
            raw_skills: list[str] = structured.get("skills", [])
            if raw_skills:
                matched = await _normalize_skills(db, user_id, raw_skills)
                structured["skills"] = matched

            # 7. ?? resume
            resume = None
            if task.file_id:
                resume = await resume_repository.get_by_user_and_id(db, task.file_id, user_id)
                if not resume:
                    resume = await resume_repository.get_by_user_and_id(db, task.file_id, user_id)
            if resume is None:
                from app.models.entities.resume import Resume
                resumes_list, _ = await resume_repository.list_by_user(db, user_id)
                for r in resumes_list:
                    if r.file_id == file_id:
                        resume = r
                        break
            if resume:
                resume.content_text = json.dumps(structured, ensure_ascii=False)
                await resume_repository.update(db, resume)

            # 7.5. ???????????????????????????
            sync_info = await _sync_parsed_to_profile(db, user_id, structured)

            # 8. ? parse_task ? SUCCESS, result ???????????????
            #    ??????????? GET /api/resume/{resume_id} ???? parsed
            task.status = "SUCCESS"
            task.result = {
                "parsed_count": len(structured.get("skills", [])) + len(structured.get("experience", [])),
                **sync_info,
            }
            await parse_task_repository.update(db, task)
            await db.commit()

        except Exception as exc:
            # ????
            try:
                task = await parse_task_repository.get_by_file_and_user(db, file_id, user_id)
                if task:
                    task.status = "FAILED"
                    task.result = {"error": str(exc)}
                    await parse_task_repository.update(db, task)
                    await db.commit()
            except Exception:
                await db.rollback()




async def _sync_parsed_to_profile(
    db: AsyncSession,
    user_id: int,
    structured: dict,
) -> dict[str, Any]:
    """?????????????????????

    ???????real_name ? education ????????????????
    ???????????????????
    ????? company+title ?????
    ???? _normalize_skills ??????????????

    Returns:
        dict: ????????????????? parse_task.result?
    """
    from app.models.entities.user_profile import UserProfile
    from app.models.entities.user_work_experience import UserWorkExperience

    # 1. ???????
    profile = await _user_profile_repository.get_by_user_id(db, user_id)
    if profile is None:
        profile = UserProfile(user_id=user_id, profile_completeness=0)
        profile = await _user_profile_repository.create(db, profile)

    # ??????????????????
    is_empty = profile.real_name is None and profile.education is None

    synced_fields: list[str] = []

    # 2. ???? ? ?????
    if profile.real_name is None and structured.get("name"):
        profile.real_name = str(structured["name"])[:50]
        synced_fields.append("real_name")
    if profile.education is None and structured.get("education"):
        profile.education = str(structured["education"])[:20]
        synced_fields.append("education")
    if profile.work_years is None and structured.get("years"):
        try:
            profile.work_years = int(structured["years"])
            synced_fields.append("work_years")
        except (ValueError, TypeError):
            pass
    if profile.current_city is None and structured.get("city"):
        profile.current_city = str(structured["city"])[:100]
        synced_fields.append("current_city")
    if profile.expected_position is None and structured.get("targetJob"):
        profile.expected_position = str(structured["targetJob"])[:200]
        synced_fields.append("expected_position")
    if profile.school is None and structured.get("school"):
        profile.school = str(structured["school"])[:100]
        synced_fields.append("school")
    if profile.major is None and structured.get("major"):
        profile.major = str(structured["major"])[:100]
        synced_fields.append("major")

    # 3. ???? ? ? company+title ????
    exp_list = structured.get("experience") or []
    exp_added = 0
    if isinstance(exp_list, list):
        for item in exp_list:
            company = item.get("company")
            if isinstance(company, list):
                company = " ".join(str(c) for c in company)
            company = (str(company) if company else "").strip()
            
            title = item.get("title")
            if isinstance(title, list):
                title = " ".join(str(t) for t in title)
            title = (str(title) if title else "").strip()
            
            if not company and not title:
                continue
            existing = await _user_work_experience_repository.find_active_by_company_title(
                db, user_id, company, title,
            )
            if existing is None:
                period = item.get("period")
                if isinstance(period, list):
                    period = " ".join(str(p) for p in period)
                period = (str(period) if period else "").strip() or None
                
                description = item.get("description")
                if isinstance(description, list):
                    description = " ".join(str(d) for d in description)
                description = (str(description) if description else "").strip() or None
                
                we = UserWorkExperience(
                    user_id=user_id,
                    title=title,
                    company=company,
                    period=period,
                    description=description,
                    sort_order=exp_added,
                )
                await _user_work_experience_repository.create(db, we)
                exp_added += 1
    if exp_added > 0:
        synced_fields.append("work_experiences")

    # 4. ???????????????? user_service._calc_completeness ???
    completeness = 0
    _W = {
        "real_name": 8, "gender": 4, "birth_date": 3,
        "education": 8, "school": 8, "major": 4,
        "current_city": 8, "expected_city": 7, "expected_salary": 8, "bio": 8,
        "skills": 5, "work_experiences": 5,
    }
    if profile.real_name: completeness += _W["real_name"]
    if profile.gender: completeness += _W["gender"]
    if profile.birth_date: completeness += _W["birth_date"]
    if profile.current_city: completeness += _W["current_city"]
    if profile.education: completeness += _W["education"]
    if profile.school: completeness += _W["school"]
    if profile.major: completeness += _W["major"]
    if profile.expected_city: completeness += _W["expected_city"]
    if profile.bio: completeness += _W["bio"]
    if profile.expected_salary_min is not None or profile.expected_salary_max is not None:
        completeness += _W["expected_salary"]
    skill_ids = await user_skill_repository.list_active_skill_ids(db, user_id)
    if skill_ids:
        completeness += _W["skills"]
    work_list = await _user_work_experience_repository.list_by_user(db, user_id)
    if work_list:
        completeness += _W["work_experiences"]

    profile.profile_completeness = min(completeness, 100)
    await _user_profile_repository.update(db, profile)

    return {
        "auto_synced": is_empty and len(synced_fields) > 0,
        "synced_to_profile": len(synced_fields) > 0,
        "synced_fields": synced_fields,
    }


async def sync_resume_to_profile(db: AsyncSession, user_id: int, resume_id: int) -> dict[str, Any]:
    """???????????????????????

    ? resume.content_text ?????????? _sync_parsed_to_profile ?????

    Returns:
        dict: ???????
    """
    resume = await resume_repository.get_by_user_and_id(db, resume_id, user_id)
    if resume is None or not resume.content_text:
        return {"synced_to_profile": False, "reason": "resume_not_found_or_empty"}

    try:
        structured = json.loads(resume.content_text)
    except (json.JSONDecodeError, TypeError):
        return {"synced_to_profile": False, "reason": "invalid_content"}

    return await _sync_parsed_to_profile(db, user_id, structured)



async def _extract_structured(
    db: AsyncSession,
    text_content: str,
    images: list[str],
) -> dict[str, Any]:
    """?? DeepSeek ???/?????????????

    ?? JSON ????? name, education, years, targetJob, city, skills[], experience[]?

    Args:
        db: ??????????????
        text_content: ?????????
        images: base64 ????????

    Returns:
        dict: ????????
    """
    prompt = """??????????????????????????????????JSON?????markdown????

?????
- name: ??
- education: ??????????"??"?
- years: ????????
- targetJob: ????
- city: ????
- skills: ???????????????????????????
  ???["Java", "Spring Boot", "MySQL", "Redis", "Docker", "Linux", "Git"]
  ??????????????????????????
- skill_proficiency: ????????????? {"name":"???","level":"??/??/??"}
- experience: ?????????? company, title, period, description?description?????

???JSON??????????????

?????
"""
    prompt += text_content

    messages = [{"role": "user", "content": prompt}]

    if images:
        image_contents = [{"type": "text", "text": prompt}]
        for img in images:
            image_contents.append({"type": "image_url", "image_url": {"url": img}})
        messages = [{"role": "user", "content": image_contents}]

    response = await deepseek_client.chat(messages, temperature=0.1, max_tokens=8192)

    try:
        clean = response.strip()
        import re as _re
        m = _re.search("```json[ \t]*\n(.+?)\n```", clean, _re.DOTALL)
        if m:
            clean = m.group(1).strip()
        else:
            if clean.startswith("```json"):
                clean = clean[7:]
            if clean.endswith("```"):
                clean = clean[:-3]
            clean = clean.strip()
        result = json.loads(clean)
    except (json.JSONDecodeError, Exception):
        result = {"raw_response": response}

    return result


async def _normalize_skills(
    db: AsyncSession,
    user_id: int,
    raw_skills: list[str],
) -> list[dict[str, Any]]:
    """???????????????? skill_id?

    ????????? user_skill ??

    Args:
        db: ??????
        user_id: ?????
        raw_skills: ????????

    Returns:
        list[dict]: ??????? name, skill_id, category?
    """
    if not raw_skills:
        return []

    norm_names = [skill_matcher.normalize_skill_name(s) for s in raw_skills]
    exact_map = await skill_repository.get_by_names(db, norm_names)
    synonym_map = await skill_synonym_repository.list_by_synonyms(db, norm_names)
    matches = skill_matcher.match_skills(norm_names, exact_map, synonym_map)

    result: list[dict[str, Any]] = []
    for norm_name, skill_id in matches.items():
        if skill_id is not None:
            skill = await skill_repository.get_by_id(db, skill_id)
            cat = skill.category if skill else None
            existing = await user_skill_repository.find_active_by_skill(db, user_id, skill_id)
            if existing is None:
                us = UserSkill(user_id=user_id, skill_id=skill_id, proficiency_level=0.0)
                await user_skill_repository.create(db, us)
            result.append({"name": norm_name, "skill_id": skill_id, "category": cat})
        else:
            cand = Skill(name=norm_name, status=SkillStatusEnum.CANDIDATE.value)
            cand = await skill_repository.create(db, cand)
            us = UserSkill(user_id=user_id, skill_id=cand.id, proficiency_level=0.0)
            await user_skill_repository.create(db, us)
            result.append({"name": norm_name, "skill_id": cand.id, "category": None})

    await db.flush()
    return result


async def run_jd_parse_pipeline(file_id: int, user_id: int) -> None:
    """JD 文件解析流水线。"""
    async with AsyncSessionLocal() as db:
        try:
            task = await parse_task_repository.get_by_file_and_user(db, file_id, user_id)
            if task is None:
                return
            task.status = "PARSING"
            await parse_task_repository.update(db, task)
            await db.commit()

            from app.repositories import upload_file_repository
            upload_entity = await upload_file_repository.get_by_id(db, file_id)
            if upload_entity is None:
                raise ValueError("upload_file 不存在")

            disk_path = file_store.resolve_path(upload_entity.path)
            raw_text = extractor.extract_text(str(disk_path))

            images = extractor.extract_images_as_base64(str(disk_path))

            structured = await _extract_jd_structured(db, raw_text, images)

            raw_skills: list[str] = structured.get("skills", [])
            if raw_skills:
                matched = await _normalize_jd_skills(db, raw_skills)
                structured["skills"] = matched

            task.status = "SUCCESS"
            task.result = structured
            await parse_task_repository.update(db, task)
            await db.commit()

        except Exception as exc:
            try:
                task = await parse_task_repository.get_by_file_and_user(db, file_id, user_id)
                if task:
                    task.status = "FAILED"
                    task.result = {"error": str(exc)}
                    await parse_task_repository.update(db, task)
                    await db.commit()
            except Exception:
                await db.rollback()


async def _extract_jd_structured(
    db: AsyncSession,
    text_content: str,
    images: list[str],
) -> dict[str, Any]:
    """通过 DeepSeek 解析 JD 文档，提取结构化信息。"""
    prompt = """请分析以下职位描述(JD)文档，提取结构化信息并以JSON格式输出，不要包含markdown格式。

提取字段：
- title: 岗位名称（如"高级前端工程师"）
- city: 工作城市
- education_requirement: 学历要求（如"本科"、"硕士"）
- experience_min: 最低工作经验年限（整数，如3表示3年以上）
- salary_min: 最低薪资（月薪，单位：元）
- salary_max: 最高薪资（月薪，单位：元）
- job_type: 工作类型（FULL_TIME/全职, PART_TIME/兼职, INTERN/实习）
- description: 职位描述文本
- benefits: 福利列表（如["五险一金", "年终奖"]）
- skills: 技能要求列表（技能名称数组）

请只输出JSON格式数据，不要包含其他内容。

文档内容：
"""
    prompt += text_content

    messages = [{"role": "user", "content": prompt}]

    if images:
        image_contents = [{"type": "text", "text": prompt}]
        for img in images:
            image_contents.append({"type": "image_url", "image_url": {"url": img}})
        messages = [{"role": "user", "content": image_contents}]

    response = await deepseek_client.chat(messages, temperature=0.1, max_tokens=8192)

    try:
        clean = response.strip()
        m = _re_module.search("```json[ \t]*\n(.+?)\n```", clean, _re_module.DOTALL)
        if m:
            clean = m.group(1).strip()
        else:
            if clean.startswith("```json"):
                clean = clean[7:]
            if clean.endswith("```"):
                clean = clean[:-3]
            clean = clean.strip()
        result = json.loads(clean)
    except (json.JSONDecodeError, Exception):
        result = {"raw_response": response}

    return result


async def _normalize_jd_skills(
    db: AsyncSession,
    raw_skills: list[str],
) -> list[dict[str, Any]]:
    """将 JD 中的技能名称归一化为 skill_id。"""
    if not raw_skills:
        return []

    norm_names = [skill_matcher.normalize_skill_name(s) for s in raw_skills]
    exact_map = await skill_repository.get_by_names(db, norm_names)
    synonym_map = await skill_synonym_repository.list_by_synonyms(db, norm_names)
    matches = skill_matcher.match_skills(norm_names, exact_map, synonym_map)

    result: list[dict[str, Any]] = []
    for norm_name, skill_id in matches.items():
        if skill_id is not None:
            skill = await skill_repository.get_by_id(db, skill_id)
            cat = skill.category if skill else None
            result.append({"name": norm_name, "skill_id": skill_id, "category": cat})
        else:
            cand = Skill(name=norm_name, status=SkillStatusEnum.CANDIDATE.value)
            cand = await skill_repository.create(db, cand)
            result.append({"name": norm_name, "skill_id": cand.id, "category": None})

    await db.flush()
    return result
