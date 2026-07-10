"""用户实体 ORM 模块。

映射 KingbaseES `zhihire` 库中已有的 `user` 表。库表使用单数名，
密码列名为 `password`（ORM 属性名保持 `password_hash`，通过 `mapped_column`
显式映射），软删除标记为 VARCHAR `'0'/'1'`。
"""
from datetime import datetime  # 时间类型注解

from sqlalchemy import BigInteger, DateTime, String, Text, func  # 列类型与 now
from sqlalchemy.orm import Mapped, mapped_column  # 2.0 声明式注解

from app.models.entities.base import Base  # 声明式基类


class User(Base):
    """用户实体，映射 `user` 表（库中原有表名）。

    沿用库中的软删除设计：`deleted_at='0'` 表示未删除，`'1'` 表示已删除，
      `deleted_at='0'` 表示未删除，`'1'` 表示已删除，
    查询时统一过滤 `.deleted_at == '0'`。

    Attributes:
        id: 用户主键，自增 BIGINT。
        username: 用户名（VARCHAR 50）。
        password_hash: ORM 属性名，实际映射到 DB 列 `password`（VARCHAR 255）。
        email: 邮箱，可空。
        phone: 手机号，可空。
        role: 角色（VARCHAR 20），默认 USER。
        status: 账号状态（VARCHAR 20），默认 NORMAL。
        avatar_url: 头像链接，可空。
        created_at: 创建时间戳。
        updated_at: 更新时间戳。
        deleted_at: 软删除标记（VARCHAR 1），`'0'` 未删 / `'1'` 已删。
    """

    __tablename__ = "user"  # 对齐库中已有表名（单数）

    # 主键：BIGINT 自增，匹配序列 user_id_seq
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    # 用户名：VARCHAR 50 唯一
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    # 密码：ORM 属性名 password_hash，实际映射到 DB 列 password
    password_hash: Mapped[str] = mapped_column("password", String(255), nullable=False)
    # 邮箱：可空
    email: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # 手机号：可空
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    # 角色：VARCHAR 语义化枚举，默认 USER
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="USER")
    # 账号状态：VARCHAR，默认 NORMAL
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="NORMAL")
    # 头像链接：可空
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # 创建时间：数据库 server 端写入
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
    )
    # 更新时间：数据库 server 端写入，行变更时自动刷新
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    # 软删除标记：VARCHAR(1)，'0' 未删 / '1' 已删（对齐库中原有设计）
    deleted_at: Mapped[str] = mapped_column(String(1), nullable=False, server_default=func.text("'0'::character varying"))

    def __repr__(self) -> str:
        """可读的调试表示。"""
        return f"<User id={self.id} username={self.username!r} role={self.role!r}>"
