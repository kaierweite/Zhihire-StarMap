"""用户档案扩展实体 ORM 模块。

映射 KingbaseES `zhihire` 库中已有的 `user_profile` 表。
求职者档案为单记录设计（一人一档），通过 `user_id` 关联到 `user` 表。
软删除标记 `deleted_at` 为 VARCHAR `'0'/'1'`。
"""
from datetime import date, datetime  # 日期与时间类型

from sqlalchemy import (  # 列类型与函数
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column  # 2.0 声明式注解

from app.models.entities.base import Base  # 声明式基类


class UserProfile(Base):
    """用户档案实体，映射 `user_profile` 表（库中表名，单数）。

    每位求职者对应唯一一条档案记录（通过 `user_id` 关联回 `user` 表）。
    档案以单记录承载基本信息、教育经历（内联 school/major/education）、
    求职意向（薪资区间、期望城市）与个人优势（bio），
    完成度 `profile_completeness` 由服务层自动计算并回写。

    Attributes:
        id: 档案主键，自增 BIGINT。
        user_id: 关联用户主键，唯一。
        real_name: 真实姓名，可空。
        gender: 性别（MALE/FEMALE/OTHER），可空。
        birth_date: 出生日期，可空。
        education: 学历（高中/专科/本科/硕士/博士），可空。
        school: 毕业院校，可空。
        major: 所学专业，可空。
        work_years: 工作年限，可空。
        expected_salary_min: 期望薪资下限，可空。
        expected_salary_max: 期望薪资上限，可空。
        expected_city: 期望城市，可空。
        current_city: 当前城市，可空。
        bio: 个人优势/自我介绍，可空。
        profile_completeness: 档案完成度 0~100，默认 0。
        created_at: 创建时间。
        updated_at: 更新时间。
        deleted_at: 软删除标记（VARCHAR 1），`'0'` 未删 / `'1'` 已删。
    """

    __tablename__ = "user_profile"  # 对齐库中已有表名

    # 主键：BIGINT 自增，匹配序列 user_profile_id_seq
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    # 关联用户主键：唯一，外键关联 user.id
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    # 真实姓名
    real_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # 性别：MALE/FEMALE/OTHER
    gender: Mapped[str | None] = mapped_column(String(10), nullable=True)
    # 出生日期
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    # 学历：高中/专科/本科/硕士/博士
    education: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # 毕业院校
    school: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # 所学专业
    major: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # 工作年限
    work_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # 期望薪资下限（DECIMAL(12,2)）
    expected_salary_min: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    # 期望薪资上限
    expected_salary_max: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    # 期望城市
    expected_city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # 当前城市
    current_city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # 个人优势/自我介绍
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 档案完成度 0~100，默认 0
    profile_completeness: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
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
    # 软删除标记：VARCHAR(1)，'0' 未删 / '1' 已删
    deleted_at: Mapped[str] = mapped_column(String(1), nullable=False, server_default=func.text("'0'::character varying"))

    def __repr__(self) -> str:
        """可读的调试表示。"""
        return f"<UserProfile id={self.id} user_id={self.user_id} completeness={self.profile_completeness}>"
