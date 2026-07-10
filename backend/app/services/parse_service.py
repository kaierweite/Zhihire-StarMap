"""???????????

BackgroundTasks ???????????
???? + ?? ? DeepSeek ??? ? ???? ? ??
"""
import json
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

            # 8. ?? parse_task ? SUCCESS
            task.status = "SUCCESS"
            task.result = structured
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
    prompt = """????????????????????????????????? JSON ???

?????
- name: ??
- education: ????
- years: ????
- targetJob: ????
- city: ????
- skills: ????????
- experience: ?????????????? company, title, period, description?

??? JSON ????????????

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
        if clean.startswith("`json"):
            clean = clean[7:]
        if clean.endswith("`"):
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
            result.append({"name": norm_name, "skill_id": cand.id, "category": None})

    await db.flush()
    return result
