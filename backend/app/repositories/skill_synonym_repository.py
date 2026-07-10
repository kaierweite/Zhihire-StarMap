"""技能同义词仓储模块。

只做原子数据库操作。软删除使用库中约定的 VARCHAR `'0'/'1'` 标记，
查询时过滤 `deleted_at == '0'` 以获得未删除记录。
"""
from sqlalchemy import select  # 查询构造
from sqlalchemy.ext.asyncio import AsyncSession  # 异步会话类型

from app.models.entities.skill_synonym import SkillSynonym  # 技能同义词 ORM


async def list_by_synonyms(db: AsyncSession, synonyms: list[str]) -> dict[str, int]:
    """批量按同义写法查询，返回 synonym -> skill_id 的映射。

    Args:
        db: 异步数据库会话。
        synonyms: 需要查询的同义写法列表。

    Returns:
        dict[str, int]: synonym -> skill_id 的映射；未命中的不在其中。
    """
    if not synonyms:
        return {}
    stmt = select(SkillSynonym.synonym, SkillSynonym.skill_id).where(
        SkillSynonym.synonym.in_(synonyms),
        SkillSynonym.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return {syn: skill_id for syn, skill_id in result.all()}
