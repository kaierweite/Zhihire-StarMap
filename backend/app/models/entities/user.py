"""用户实体 ORM 模块。

定义 `users` 表结构与 `User` ORM 类，承载账号、凭据、角色与状态等核心字段。
所有状态、角色字段统一使用 VARCHAR 语义化大写枚举，遵循项目统一约定。
"""
from datetime import datetime  # 时间类型注解

from sqlalchemy import BigInteger, DateTime, String, func  # 列类型与 now 表达式
from sqlalchemy.orm import Mapped, mapped_column  # 2.0 声明式注解

from app.models.entities.base import Base  # 声明式基类
from app.models.enums.role import RoleEnum  # 角色枚举（默认值来源）
from app.models.enums.status import UserStatusEnum  # 用户状态枚举（默认值来源）


class User(Base):
    """用户实体，对应 `users` 表。

    采用软删除策略：删除时写入 `deleted_at`，查询时过滤已删除记录。

    Attributes:
        id: 用户主键，自增。
        username: 用户名，唯一索引。
        password_hash: 密码哈希（bcrypt），不存明文。
        role: 角色，VARCHAR 大写枚举（ADMIN/USER/COMPANY）。
        email: 邮箱，可空。
        phone: 手机号，可空。
        status: 账号状态，VARCHAR 大写枚举（NORMAL/DISABLED/BANNED）。
        created_at: 创建时间。
        updated_at: 更新时间。
        deleted_at: 软删除标记，未删除时为 NULL。
    """

    __tablename__ = "users"  # 表名复数，遵循统一约定

    # 主键：自增大整数，预留海量用户空间
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    # 用户名：唯一索引，长度 64
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    # 密码哈希：bcrypt 输出固定长度，容纳 128 以防扩展
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    # 角色：VARCHAR 语义化枚举，默认求职者
    role: Mapped[str] = mapped_column(String(16), nullable=False, default=RoleEnum.USER.value)
    # 邮箱：可空
    email: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # 手机号：可空
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    # 账号状态：VARCHAR 语义化枚举，默认正常
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=UserStatusEnum.NORMAL.value,
    )
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
    # 软删除时间：NULL 表示未删除
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)

    def __repr__(self) -> str:
        """可读的调试表示。"""
        # 简洁展示主键与用户名
        return f"<User id={self.id} username={self.username!r} role={self.role!r}>"
