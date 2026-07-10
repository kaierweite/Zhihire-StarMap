"""用户项目经历仓储模块。"""
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.user_project_experience import UserProjectExperience


async def list_by_user(db: AsyncSession, user_id: int) -> list[UserProjectExperience]:
    stmt = select(UserProjectExperience).where(
        UserProjectExperience.user_id == user_id,
        UserProjectExperience.deleted_at == "0",
    ).order_by(UserProjectExperience.sort_order, UserProjectExperience.id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create(db: AsyncSession, obj: UserProjectExperience) -> UserProjectExperience:
    db.add(obj)
    await db.flush()
    return obj


async def soft_delete_all_by_user(db: AsyncSession, user_id: int) -> None:
    await db.execute(
        update(UserProjectExperience)
        .where(UserProjectExperience.user_id == user_id, UserProjectExperience.deleted_at == "0")
        .values(deleted_at="1")
    )
