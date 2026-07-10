"""企业实体 ORM 模块。

定义 `companies` 表与 `Company` ORM 类，企业用户注册时关联创建一条记录，
初始审核状态为 `UNVERIFIED`。
"""
from datetime import datetime  # 时间类型注解

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func  # 列类型与外键
from sqlalchemy.orm import Mapped, mapped_column  # 2.0 声明式注解

from app.models.entities.base import Base  # 声明式基类
from app.models.enums.status import CompanyAuditStatusEnum  # 审核状态枚举（默认值来源）


class Company(Base):
    """企业实体，对应 `companies` 表。

    一个企业用户（`users.role == COMPANY`）对应一条企业信息记录，
    通过 `user_id` 外键关联回 `users.id`。

    Attributes:
        id: 企业主键，自增。
        user_id: 关联用户主键，唯一。
        company_name: 企业名称。
        audit_status: 审核状态，默认 UNVERIFIED。
        contact_email: 联系邮箱，可空。
        contact_phone: 联系电话，可空。
        created_at: 创建时间。
        updated_at: 更新时间。
        deleted_at: 软删除标记，NULL 表示未删除。
    """

    __tablename__ = "companies"  # 表名复数，遵循统一约定

    # 主键：自增大整数
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    # 关联用户主键：唯一，一个企业用户仅一条企业信息记录
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    # 企业名称：长度 128
    company_name: Mapped[str] = mapped_column(String(128), nullable=False)
    # 审核状态：默认未审核
    audit_status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=CompanyAuditStatusEnum.UNVERIFIED.value,
    )
    # 联系邮箱：可空
    contact_email: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # 联系电话：可空
    contact_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    # 创建时间：数据库 server 端写入
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
    )
    # 更新时间：行变更时自动刷新
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    # 软删除时间
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)

    def __repr__(self) -> str:
        """可读的调试表示。"""
        return f"<Company id={self.id} user_id={self.user_id} name={self.company_name!r}>"
