"""企业实体 ORM 模块。

映射 KingbaseES `zhihire` 库中已有的 `company` 表。企业用户注册时关联创建一条记录，
初始审核状态为 `UNVERIFIED`。软删除标记为 VARCHAR `'0'/'1'`。
"""
from datetime import datetime  # 时间类型注解

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func  # 列类型与外键
from sqlalchemy.orm import Mapped, mapped_column  # 2.0 声明式注解

from app.models.entities.base import Base  # 声明式基类


class Company(Base):
    """企业实体，映射 `company` 表（库中原有表名，单数）。

    一个企业用户（`user.role == COMPANY`）对应一条企业信息记录，
    通过 `user_id` 外键关联回 `user.id`。

    Attributes:
        id: 企业主键，自增 BIGINT。
        user_id: 关联用户主键，唯一。
        company_name: 企业名称。
        industry: 所属行业，可空。
        scale: 企业规模，可空。
        website: 企业网站，可空。
        logo_url: 企业 Logo 链接，可空。
        description: 企业介绍，可空。
        address: 企业地址，可空。
        contact_name: 联系人姓名，可空。
        contact_phone: 联系电话，可空。
        contact_email: 联系邮箱，可空。
        audit_status: 审核状态，默认 UNVERIFIED。
        audit_reason: 审核驳回原因，可空。
        created_at: 创建时间。
        updated_at: 更新时间。
        deleted_at: 软删除标记（VARCHAR 1），`'0'` 未删 / `'1'` 已删。
    """

    __tablename__ = "company"  # 对齐库中已有表名（单数）

    # 主键：BIGINT 自增，匹配序列 company_id_seq
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    # 关联用户主键：唯一
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    # 企业名称
    company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    # 所属行业
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # 企业规模
    scale: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # 企业类型（国企/事业单位/上市公司/其他）
    company_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # 企业网站
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Logo 链接
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # 企业介绍
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 企业地址
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # 联系人姓名
    contact_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # 联系电话
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # 联系邮箱
    contact_email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # 审核状态：默认未审核
    audit_status: Mapped[str] = mapped_column(String(20), nullable=False, default="UNVERIFIED")
    # 驳回原因
    audit_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 创建时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
    )
    # 更新时间
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
        return f"<Company id={self.id} user_id={self.user_id} name={self.company_name!r}>"
