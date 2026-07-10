"""职业规划仓储模块。

只做原子数据库操作。软删除使用 VARCHAR `'0'/'1'` 标记，
查询时过滤 `deleted_at == '0'` 以获得未删除记录。
"""
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities.career_plan import CareerPlan


async def get_by_user(db: AsyncSession, user_id: int) -> CareerPlan | None:
    """查询某用户最新的一条职业规划。

    Args:
        db: 异步数据库会话。
        user_id: 用户主键。

    Returns:
        CareerPlan | None: 最新的规划记录，或 None。
    """
    stmt = (
        select(CareerPlan)
        .where(CareerPlan.user_id == user_id, CareerPlan.deleted_at == "0")
        .order_by(CareerPlan.updated_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_user_and_role(db: AsyncSession, user_id: int, role_id: int) -> CareerPlan | None:
    """查询某用户对某角色的规划记录。

    Args:
        db: 异步数据库会话。
        user_id: 用户主键。
        role_id: 目标角色主键。

    Returns:
        CareerPlan | None: 规划记录，或 None。
    """
    stmt = (
        select(CareerPlan)
        .where(
            CareerPlan.user_id == user_id,
            CareerPlan.target_role_id == role_id,
            CareerPlan.deleted_at == "0",
        )
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def upsert(db: AsyncSession, plan: CareerPlan) -> CareerPlan:
    """新增或更新职业规划记录。

    若同一 user_id + target_role_id 已存在，则更新 plan_content 和 source；
    否则新增。

    Args:
        db: 异步数据库会话。
        plan: 待保存的 CareerPlan 实例。

    Returns:
        CareerPlan: 已写入数据库、含主键的实例。
    """
    existing = await get_by_user_and_role(db, plan.user_id, plan.target_role_id)
    if existing:
        existing.target_role = plan.target_role
        existing.plan_content = plan.plan_content
        existing.source = plan.source
        existing.deleted_at = "0"
        await db.flush()
        return existing
    else:
        db.add(plan)
        await db.flush()
        return plan


async def soft_delete(db: AsyncSession, user_id: int, role_id: int) -> None:
    """软删除某用户对某角色的规划记录。

    Args:
        db: 异步数据库会话。
        user_id: 用户主键。
        role_id: 目标角色主键。
    """
    stmt = (
        update(CareerPlan)
        .where(
            CareerPlan.user_id == user_id,
            CareerPlan.target_role_id == role_id,
            CareerPlan.deleted_at == "0",
        )
        .values(deleted_at="1")
    )
    await db.execute(stmt)
    await db.flush()