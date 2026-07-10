"""状态枚举模块。

所有状态字段统一使用 VARCHAR 语义化大写枚举，而非 INT 编码。
"""
from enum import Enum  # 标准枚举基类


class UserStatusEnum(str, Enum):
    """用户账号状态枚举。"""

    NORMAL = "NORMAL"  # 正常
    DISABLED = "DISABLED"  # 已停用（管理员手动禁用）
    BANNED = "BANNED"  # 已封禁（违规处罚）


class GenericStatusEnum(str, Enum):
    """通用启用状态枚举。

    适用于岗位、技能、通知等仅需启用/停用判断的实体。
    """

    NORMAL = "NORMAL"  # 启用
    DISABLED = "DISABLED"  # 停用