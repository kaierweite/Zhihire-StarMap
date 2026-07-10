"""角色枚举模块。

统一以大写 VARCHAR 语义化字符串存储角色，避免 INT 枚举带来的可读性问题。
"""
from enum import Enum  # 标准枚举基类


class RoleEnum(str, Enum):
    """用户角色枚举。

    采用 str + Enum 继承，便于直接序列化为字符串并参与 JWT claim。
    所有角色值统一大写。
    """

    ADMIN = "ADMIN"  # 平台管理员
    USER = "USER"  # 普通求职者
    COMPANY = "COMPANY"  # 企业用户


# 合法的角色值集合，供守卫快速校验
VALID_ROLES = frozenset(member.value for member in RoleEnum)