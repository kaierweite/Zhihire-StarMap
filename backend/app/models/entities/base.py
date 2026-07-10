"""ORM 声明式基类模块。

所有实体模型统一继承 `Base`，Alembic 的 `target_metadata` 指向 `Base.metadata`，
从而在一次 `alembic revision --autogenerate` 中捕获全部表结构变更。
"""
from sqlalchemy.orm import DeclarativeBase  # SQLAlchemy 2.0 声明式基类


class Base(DeclarativeBase):
    """所有 ORM 实体的公共声明式基类。

    继承自 SQLAlchemy 2.0 的 DeclarativeBase，
    使得各实体共享同一份 MetaData，便于迁移工具统一管理。
    """

    pass
