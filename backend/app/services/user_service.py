"""用户档案业务服务模块。

编排求职者个人档案的读取与更新：
- get_profile：汇总 user + user_profile + user_skill JOIN skill 及 4 张子表
- update_profile：逐 section 更新；多值字段（工作/项目/语言/证书）使用全量替换策略
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.normalize import skill_matcher
from app.models.entities.skill import Skill
from app.models.entities.user import User
from app.models.entities.user_profile import UserProfile
from app.models.entities.user_skill import UserSkill
from app.models.entities.user_work_experience import UserWorkExperience
from app.models.entities.user_project_experience import UserProjectExperience
from app.models.entities.user_language import UserLanguage
from app.models.entities.user_certificate import UserCertificate
from app.models.enums.status import SkillStatusEnum
from app.models.schemas.user import (
    CertificateItem,
    LanguageItem,
    ProjectExperienceItem,
    SkillItem,
    UserProfileDTO,
    UserProfileUpdateForm,
    WorkExperienceItem,
)
from app.repositories import (
    skill_repository,
    skill_synonym_repository,
    user_skill_repository,
    user_profile_repository,
    user_work_experience_repository,
    user_project_experience_repository,
    user_language_repository,
    user_certificate_repository,
)
from app.services.errors import BusinessError

# ====== 档案完成度权重 ======
_COMPLETENESS_WEIGHTS: dict[str, int] = {
    "real_name": 8,
    "gender": 4,
    "birth_date": 3,
    "phone": 8,
    "education": 8,
    "school": 8,
    "major": 4,
    "current_city": 8,
    "expected_city": 7,
    "expected_salary": 8,
    "bio": 8,
    "skills": 5,
    "work_experiences": 5,
    "project_experiences": 5,
    "languages": 4,
    "certificates": 4,
}
_SALARY_K = 1000


def _calc_completeness(profile: UserProfile, skill_count: int) -> int:
    total = 0
    if profile.real_name: total += _COMPLETENESS_WEIGHTS["real_name"]
    if profile.gender: total += _COMPLETENESS_WEIGHTS["gender"]
    if profile.birth_date: total += _COMPLETENESS_WEIGHTS["birth_date"]
    if profile.current_city: total += _COMPLETENESS_WEIGHTS["current_city"]
    if profile.expected_city: total += _COMPLETENESS_WEIGHTS["expected_city"]
    if profile.bio: total += _COMPLETENESS_WEIGHTS["bio"]
    if profile.education: total += _COMPLETENESS_WEIGHTS["education"]
    if profile.school: total += _COMPLETENESS_WEIGHTS["school"]
    if profile.major: total += _COMPLETENESS_WEIGHTS["major"]
    if profile.expected_salary_min is not None or profile.expected_salary_max is not None:
        total += _COMPLETENESS_WEIGHTS["expected_salary"]
    if skill_count > 0:
        total += _COMPLETENESS_WEIGHTS["skills"]
    return min(total, 100)


def _calc_completeness_for_update(profile: UserProfile, user: User, has_skills: bool) -> int:
    total = _calc_completeness(profile, 1 if has_skills else 0)
    if user.phone:
        total += _COMPLETENESS_WEIGHTS["phone"]
    return min(total, 100)


async def _get_or_create_profile(db: AsyncSession, user_id: int) -> UserProfile:
    profile = await user_profile_repository.get_by_user_id(db, user_id)
    if profile is None:
        profile = UserProfile(user_id=user_id, profile_completeness=0)
        profile = await user_profile_repository.create(db, profile)
        await db.flush()
    return profile


# ====== 子表全量替换辅助 ======
async def _replace_work_experiences(db: AsyncSession, user_id: int, items: list[dict]) -> None:
    await user_work_experience_repository.soft_delete_all_by_user(db, user_id)
    for idx, item in enumerate(items):
        obj = UserWorkExperience(
            user_id=user_id,
            title=item.get("title", ""),
            company=item.get("company", ""),
            period=item.get("period"),
            description=item.get("description"),
            sort_order=idx,
        )
        await user_work_experience_repository.create(db, obj)


async def _replace_project_experiences(db: AsyncSession, user_id: int, items: list[dict]) -> None:
    await user_project_experience_repository.soft_delete_all_by_user(db, user_id)
    for idx, item in enumerate(items):
        obj = UserProjectExperience(
            user_id=user_id,
            name=item.get("name", ""),
            description=item.get("description"),
            sort_order=idx,
        )
        await user_project_experience_repository.create(db, obj)


async def _replace_languages(db: AsyncSession, user_id: int, items: list[dict]) -> None:
    await user_language_repository.soft_delete_all_by_user(db, user_id)
    for idx, item in enumerate(items):
        obj = UserLanguage(
            user_id=user_id,
            language=item.get("name", ""),
            level=item.get("level"),
            sort_order=idx,
        )
        await user_language_repository.create(db, obj)


async def _replace_certificates(db: AsyncSession, user_id: int, items: list[dict]) -> None:
    await user_certificate_repository.soft_delete_all_by_user(db, user_id)
    for idx, item in enumerate(items):
        obj = UserCertificate(
            user_id=user_id,
            name=item.get("name", ""),
            sort_order=idx,
        )
        await user_certificate_repository.create(db, obj)


# ====== 主业务流程 ======
async def get_profile(db: AsyncSession, user: User) -> UserProfileDTO:
    profile = await _get_or_create_profile(db, user.id)
    rows = await user_skill_repository.list_by_user(db, user.id)
    skills = [
        SkillItem(skill_id=us.skill_id, name=sk.name, category=sk.category, proficiency_level=us.proficiency_level)
        for us, sk in rows
    ]
    work_rows = await user_work_experience_repository.list_by_user(db, user.id)
    project_rows = await user_project_experience_repository.list_by_user(db, user.id)
    lang_rows = await user_language_repository.list_by_user(db, user.id)
    cert_rows = await user_certificate_repository.list_by_user(db, user.id)

    return UserProfileDTO(
        id=user.id,
        username=user.username,
        avatar_url=user.avatar_url,
        real_name=profile.real_name,
        gender=profile.gender,
        birth_date=profile.birth_date,
        phone=user.phone,
        email=user.email,
        education=profile.education,
        school=profile.school,
        major=profile.major,
        work_years=profile.work_years,
        current_city=profile.current_city,
        expected_city=profile.expected_city,
        expected_position=profile.expected_position,
        expected_worktype=profile.expected_worktype,
        expected_industry=profile.expected_industry,
        expected_salary_min=float(profile.expected_salary_min) if profile.expected_salary_min is not None else None,
        expected_salary_max=float(profile.expected_salary_max) if profile.expected_salary_max is not None else None,
        bio=profile.bio,
        work_experiences=[
            WorkExperienceItem(title=w.title, company=w.company, period=w.period, description=w.description)
            for w in work_rows
        ],
        project_experiences=[
            ProjectExperienceItem(name=p.name, description=p.description)
            for p in project_rows
        ],
        languages=[
            LanguageItem(name=l.language, level=l.level)
            for l in lang_rows
        ],
        certificates=[
            CertificateItem(name=c.name)
            for c in cert_rows
        ],
        profile_completeness=profile.profile_completeness,
        skills=skills,
        created_at=profile.created_at,
    )


async def update_profile(db: AsyncSession, user: User, form: UserProfileUpdateForm) -> UserProfileDTO:
    # 薪资一致性校验（K 值）
    if (
        form.expected_salary_min is not None
        and form.expected_salary_max is not None
        and form.expected_salary_min > form.expected_salary_max
    ):
        raise BusinessError(400, "期望薪资下限不能大于上限")

    profile = await _get_or_create_profile(db, user.id)

    # 标量字段覆盖
    if form.real_name is not None: profile.real_name = form.real_name
    if form.gender is not None: profile.gender = form.gender
    if form.birth_date is not None: profile.birth_date = form.birth_date
    if form.education is not None: profile.education = form.education
    if form.school is not None: profile.school = form.school
    if form.major is not None: profile.major = form.major
    if form.work_years is not None: profile.work_years = form.work_years
    if form.current_city is not None: profile.current_city = form.current_city
    if form.expected_city is not None: profile.expected_city = form.expected_city
    if form.expected_position is not None: profile.expected_position = form.expected_position
    if form.expected_worktype is not None: profile.expected_worktype = form.expected_worktype
    if form.expected_industry is not None: profile.expected_industry = form.expected_industry
    if form.bio is not None: profile.bio = form.bio
    # 薪资 K → 实际值
    if form.expected_salary_min is not None: profile.expected_salary_min = form.expected_salary_min * _SALARY_K
    if form.expected_salary_max is not None: profile.expected_salary_max = form.expected_salary_max * _SALARY_K

    # 用户主表字段
    if form.phone is not None: user.phone = form.phone
    if form.email is not None: user.email = form.email

    # 技能全量替换
    has_skills = len(await user_skill_repository.list_active_skill_ids(db, user.id)) > 0
    if form.skills is not None:
        has_skills = await _replace_user_skills(db, user.id, form.skills)

    # 子表全量替换
    if form.work_experiences is not None:
        await _replace_work_experiences(db, user.id, form.work_experiences)
    if form.project_experiences is not None:
        await _replace_project_experiences(db, user.id, form.project_experiences)
    if form.languages is not None:
        await _replace_languages(db, user.id, form.languages)
    if form.certificates is not None:
        await _replace_certificates(db, user.id, form.certificates)

    await user_profile_repository.update(db, profile)
    await db.flush()

    profile.profile_completeness = _calc_completeness_for_update(profile, user, has_skills)
    await db.flush()
    await db.commit()

    return await get_profile(db, user)


async def _replace_user_skills(db: AsyncSession, user_id: int, raw_skill_names: list[str]) -> bool:
    """全量替换用户的技能关联。"""
    seen: set[str] = set()
    norm_names: list[str] = []
    for raw in raw_skill_names:
        norm = skill_matcher.normalize_skill_name(raw)
        if norm and norm not in seen:
            seen.add(norm)
            norm_names.append(norm)

    if not norm_names:
        current = await user_skill_repository.list_active_skill_ids(db, user_id)
        for sid in current:
            us = await user_skill_repository.find_active_by_skill(db, user_id, sid)
            if us is not None:
                await user_skill_repository.soft_delete(db, us)
        return False

    exact_map = await skill_repository.get_by_names(db, norm_names)
    synonym_map = await skill_synonym_repository.list_by_synonyms(db, norm_names)
    matches = skill_matcher.match_skills(norm_names, exact_map, synonym_map)

    target_ids: list[int] = []
    for norm, skill_id in matches.items():
        if skill_id is not None:
            target_ids.append(skill_id)
        else:
            cand = Skill(name=norm, status=SkillStatusEnum.CANDIDATE.value)
            cand = await skill_repository.create(db, cand)
            target_ids.append(cand.id)

    target_set = set(target_ids)
    current_ids = set(await user_skill_repository.list_active_skill_ids(db, user_id))

    for sid in current_ids - target_set:
        us = await user_skill_repository.find_active_by_skill(db, user_id, sid)
        if us is not None:
            await user_skill_repository.soft_delete(db, us)
    for sid in target_set - current_ids:
        us = UserSkill(user_id=user_id, skill_id=sid, proficiency_level=0.0)
        await user_skill_repository.create(db, us)

    return len(target_set) > 0
