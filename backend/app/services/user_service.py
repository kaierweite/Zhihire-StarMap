"""用户档案业务服务模块。

编排求职者个人档案的读取与更新：
- get_profile：汇总 user + user_profile + user_skill JOIN skill 构造完整档案 DTO
- update_profile：逐 section 更新扩展表与 user 表，技能经 core 归一后写入 user_skill，
  并自动计算档案完成度 profile_completeness

事务提交由本层负责，仓储层仅做原子数据访问。
"""
from sqlalchemy.ext.asyncio import AsyncSession  # 异步会话类型

from app.core.normalize import skill_matcher  # 技能归一核心算法
from app.models.entities.skill import Skill  # 技能字典 ORM
from app.models.entities.user import User  # 用户 ORM
from app.models.entities.user_profile import UserProfile  # 用户档案 ORM
from app.models.entities.user_skill import UserSkill  # 用户技能关联 ORM
from app.models.enums.status import SkillStatusEnum  # 技能状态枚举
from app.models.schemas.user import (  # 请求/响应模型
    SkillItem,
    UserProfileDTO,
    UserProfileUpdateForm,
)
from app.repositories import (  # 仓储层
    skill_repository,
    skill_synonym_repository,
    user_repository,
    user_skill_repository,
    user_profile_repository,
)
from app.services.errors import BusinessError  # 业务异常


# ====== 档案完成度计算 ======
# 各字段分值之和为 100，覆盖前端展示的核心 section
_COMPLETENESS_WEIGHTS: dict[str, int] = {
    "real_name": 10,
    "gender": 5,
    "birth_date": 5,
    "phone": 10,
    "education": 10,
    "school": 10,
    "major": 5,
    "current_city": 10,
    "expected_city": 10,
    "expected_salary": 10,
    "bio": 10,
    "skills": 5,
}


def _calc_completeness(profile: UserProfile, skill_count: int) -> int:
    """根据档案字段填充情况计算完成度（0~100）。

    Args:
        profile: 用户档案实例。
        skill_count: 用户已关联的技能数量。

    Returns:
        int: 完成度，0~100。
    """
    total = 0
    # 基本信息类字段：非空即得分
    if profile.real_name:
        total += _COMPLETENESS_WEIGHTS["real_name"]
    if profile.gender:
        total += _COMPLETENESS_WEIGHTS["gender"]
    if profile.birth_date:
        total += _COMPLETENESS_WEIGHTS["birth_date"]
    if profile.current_city:
        total += _COMPLETENESS_WEIGHTS["current_city"]
    if profile.expected_city:
        total += _COMPLETENESS_WEIGHTS["expected_city"]
    if profile.bio:
        total += _COMPLETENESS_WEIGHTS["bio"]
    # 教育 section：学历与院校为主，专业为辅
    if profile.education:
        total += _COMPLETENESS_WEIGHTS["education"]
    if profile.school:
        total += _COMPLETENESS_WEIGHTS["school"]
    if profile.major:
        total += _COMPLETENESS_WEIGHTS["major"]
    # 薪资意向：下限或上限任一填写即得分
    if profile.expected_salary_min is not None or profile.expected_salary_max is not None:
        total += _COMPLETENESS_WEIGHTS["expected_salary"]
    # 技能：至少关联一个技能即得分
    if skill_count > 0:
        total += _COMPLETENESS_WEIGHTS["skills"]
    # 手机号取自 user 表，此处由调用方传入
    return min(total, 100)


def _calc_completeness_for_update(
    profile: UserProfile, user: User, has_skills: bool
) -> int:
    """更新场景下的完成度计算，额外纳入 user.phone。

    Args:
        profile: 用户档案实例（已应用更新值）。
        user: 用户实例（包含 phone 字段）。
        has_skills: 更新后是否仍有技能关联。

    Returns:
        int: 完成度 0~100。
    """
    total = _calc_completeness(profile, 1 if has_skills else 0)
    if user.phone:
        total += _COMPLETENESS_WEIGHTS["phone"]
    return min(total, 100)


async def _get_or_create_profile(db: AsyncSession, user_id: int) -> UserProfile:
    """获取用户档案；不存在则创建空档案（首次访问）。

    Args:
        db: 异步数据库会话。
        user_id: 用户主键。

    Returns:
        UserProfile: 用户档案实例。
    """
    profile = await user_profile_repository.get_by_user_id(db, user_id)
    if profile is None:
        # 首次访问：初始化一条空白档案
        profile = UserProfile(user_id=user_id, profile_completeness=0)
        profile = await user_profile_repository.create(db, profile)
        await db.flush()
    return profile


async def get_profile(db: AsyncSession, user: User) -> UserProfileDTO:
    """读取用户完整档案。

    Args:
        db: 异步数据库会话。
        user: 当前用户 ORM 实例。

    Returns:
        UserProfileDTO: 完整档案 DTO。
    """
    # 获取或初始化档案扩展记录
    profile = await _get_or_create_profile(db, user.id)
    # 查询用户技能关联及技能元信息
    rows = await user_skill_repository.list_by_user(db, user.id)
    # 转为响应模型列表
    skills = [
        SkillItem(
            skill_id=us.skill_id,
            name=sk.name,
            category=sk.category,
            proficiency_level=us.proficiency_level,
        )
        for us, sk in rows
    ]
    # 组装完整档案 DTO
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
        expected_salary_min=float(profile.expected_salary_min) if profile.expected_salary_min is not None else None,
        expected_salary_max=float(profile.expected_salary_max) if profile.expected_salary_max is not None else None,
        bio=profile.bio,
        profile_completeness=profile.profile_completeness,
        skills=skills,
        created_at=profile.created_at,
    )


async def update_profile(
    db: AsyncSession, user: User, form: UserProfileUpdateForm
) -> UserProfileDTO:
    """更新用户档案（逐 section 更新）。

    扩展表字段：仅覆盖已提供（非 None）的字段；技能列表：全量替换。
    技能名经 core 归一后写入 user_skill，未命中则创建候选技能。
    更新后自动计算并回写 profile_completeness。

    Args:
        db: 异步数据库会话。
        user: 当前用户 ORM 实例。
        form: 档案更新表单。

    Returns:
        UserProfileDTO: 更新后的完整档案 DTO。

    Raises:
        BusinessError: 薪资区间非法（下限大于上限，400）。
    """
    # 薪资区间一致性校验
    if (
        form.expected_salary_min is not None
        and form.expected_salary_max is not None
        and form.expected_salary_min > form.expected_salary_max
    ):
        raise BusinessError(400, "期望薪资下限不能大于上限")

    # 获取或初始化档案记录
    profile = await _get_or_create_profile(db, user.id)

    # 逐字段覆盖扩展表（仅覆盖已提供字段）
    if form.real_name is not None:
        profile.real_name = form.real_name
    if form.gender is not None:
        profile.gender = form.gender
    if form.birth_date is not None:
        profile.birth_date = form.birth_date
    if form.education is not None:
        profile.education = form.education
    if form.school is not None:
        profile.school = form.school
    if form.major is not None:
        profile.major = form.major
    if form.work_years is not None:
        profile.work_years = form.work_years
    if form.current_city is not None:
        profile.current_city = form.current_city
    if form.expected_city is not None:
        profile.expected_city = form.expected_city
    if form.expected_salary_min is not None:
        profile.expected_salary_min = form.expected_salary_min
    if form.expected_salary_max is not None:
        profile.expected_salary_max = form.expected_salary_max
    if form.bio is not None:
        profile.bio = form.bio

    # 用户主表字段覆盖（phone/email）
    if form.phone is not None:
        user.phone = form.phone
    if form.email is not None:
        user.email = form.email

    # 技能section：全量替换
    has_skills = bool(rows_for_skills) if "rows_for_skills" in dir() else False
    if form.skills is not None:
        has_skills = await _replace_user_skills(db, user.id, form.skills)

    # 更新扩展表
    await user_profile_repository.update(db, profile)
    # 用户主表 flush
    await db.flush()

    # 计算并回写完成度
    profile.profile_completeness = _calc_completeness_for_update(profile, user, has_skills)
    await db.flush()

    # 提交事务
    await db.commit()

    # 重新查询返回完整档案
    # 重新加载已提交后的档案与技能，避免过期状态
    return await get_profile(db, user)


async def _replace_user_skills(
    db: AsyncSession, user_id: int, raw_skill_names: list[str]
) -> bool:
    """全量替换用户的技能关联。

    流程：
      1. 对输入技能名做归一化；
      2. 批量查 skill.name 精确匹配 + skill_synonym 映射；
      3. 未命中的创建候选技能（status=CANDIDATE）；
      4. 与当前关联做差集：新增缺失、软删多余的、保留交集；
      5. 返回更新后是否仍有技能关联。

    Args:
        db: 异步数据库会话。
        user_id: 用户主键。
        raw_skill_names: 用户提交的技能名列表。

    Returns:
        bool: 更新后是否仍有至少一个技能关联。
    """
    # 去重并归一化（保留非空）
    seen: set[str] = set()
    norm_names: list[str] = []
    for raw in raw_skill_names:
        norm = skill_matcher.normalize_skill_name(raw)
        if norm and norm not in seen:
            seen.add(norm)
            norm_names.append(norm)

    # 无技能：软删当前全部关联
    if not norm_names:
        current = await user_skill_repository.list_active_skill_ids(db, user_id)
        for sid in current:
            us = await user_skill_repository.find_active_by_skill(db, user_id, sid)
            if us is not None:
                await user_skill_repository.soft_delete(db, us)
        return False

    # 批量精确匹配 skill.name
    exact_map = await skill_repository.get_by_names(db, norm_names)
    # 批量同义词映射
    synonym_map = await skill_synonym_repository.list_by_synonyms(db, norm_names)

    # 归一决策：name -> skill_id（None 表示需新建候选）
    matches = skill_matcher.match_skills(norm_names, exact_map, synonym_map)

    # 为未命中的技能创建候选技能
    for name, skill in exact_map.items():
        # 确保 exact_map 中的 Skill 实例已含 id
        if skill.id is None:
            await db.flush()

    target_skill_ids: list[int] = []
    for norm, skill_id in matches.items():
        if skill_id is not None:
            target_skill_ids.append(skill_id)
        else:
            # 创建候选技能
            candidate = Skill(
                name=norm,
                status=SkillStatusEnum.CANDIDATE.value,
                category=None,
            )
            candidate = await skill_repository.create(db, candidate)
            target_skill_ids.append(candidate.id)

    # 去重目标技能主键（同义/精确可能指向同一技能）
    target_set: set[int] = set(target_skill_ids)

    # 当前关联集合
    current_ids = set(await user_skill_repository.list_active_skill_ids(db, user_id))

    # 差集：需软删的（当前有但目标集没有）
    to_remove = current_ids - target_set
    # 差集：需新增的（目标集有但当前没有）
    to_add = target_set - current_ids

    # 软删多余的
    for sid in to_remove:
        us = await user_skill_repository.find_active_by_skill(db, user_id, sid)
        if us is not None:
            await user_skill_repository.soft_delete(db, us)

    # 新增缺失的
    for sid in to_add:
        us = UserSkill(user_id=user_id, skill_id=sid, proficiency_level=0.0)
        await user_skill_repository.create(db, us)

    return len(target_set) > 0
