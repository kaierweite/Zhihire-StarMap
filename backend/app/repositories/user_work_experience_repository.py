"""用户工作/实习经历仓储模块。"""
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.user_work_experience import UserWorkExperience


async def list_by_user(db: AsyncSession, user_id: int) -> list[UserWorkExperience]:
    stmt = select(UserWorkExperience).where(
        UserWorkExperience.user_id == user_id,
        UserWorkExperience.deleted_at == "0",
    ).order_by(UserWorkExperience.sort_order, UserWorkExperience.id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create(db: AsyncSession, obj: UserWorkExperience) -> UserWorkExperience:
    db.add(obj)
    await db.flush()
    return obj


async def soft_delete_all_by_user(db: AsyncSession, user_id: int) -> None:
    await db.execute(
        update(UserWorkExperience)
        .where(UserWorkExperience.user_id == user_id, UserWorkExperience.deleted_at == "0")
        .values(deleted_at="1")
    )


async def find_active_by_company_title(
    db: AsyncSession, user_id: int, company: str, title: str,
) -> UserWorkExperience | None:
    """????+??????????????????"""
    stmt = select(UserWorkExperience).where(
        UserWorkExperience.user_id == user_id,
        UserWorkExperience.company == company,
        UserWorkExperience.title == title,
        UserWorkExperience.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
