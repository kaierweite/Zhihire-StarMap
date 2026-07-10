"""枚举模块包。

集中导出角色枚举与状态枚举，供 ORM 与业务层统一引用。
"""
from app.models.enums.role import RoleEnum, VALID_ROLES  # 角色枚举及校验集合
from app.models.enums.status import (  # 状态枚举
    CompanyAuditStatusEnum,
    EducationEnum,
    GenderEnum,
    GenericStatusEnum,
    SkillStatusEnum,
    UserStatusEnum,
)

__all__ = [
    "RoleEnum",
    "VALID_ROLES",
    "UserStatusEnum",
    "GenericStatusEnum",
    "CompanyAuditStatusEnum",
    "SkillStatusEnum",
    "GenderEnum",
    "EducationEnum",
]
