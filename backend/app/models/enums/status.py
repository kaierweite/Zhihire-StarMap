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


class CompanyAuditStatusEnum(str, Enum):
    """企业审核状态枚举。

    用于企业用户注册后的资质审核流转。
    """

    UNVERIFIED = "UNVERIFIED"  # 未提交审核（注册后默认状态）
    PENDING = "PENDING"  # 审核中
    VERIFIED = "VERIFIED"  # 审核通过
    REJECTED = "REJECTED"  # 审核驳回


class SkillStatusEnum(str, Enum):
    """技能字典三态枚举。

    ACTIVE 启用、CANDIDATE 待审（用户归一时新创建的候选技能）、
    MERGED 已并入目标技能（不再独立使用）。
    """

    ACTIVE = "ACTIVE"  # 启用
    CANDIDATE = "CANDIDATE"  # 待审候选
    MERGED = "MERGED"  # 已合并


class GenderEnum(str, Enum):
    """性别枚举（与库中 user_profile.gender 对齐）。"""

    MALE = "MALE"  # 男
    FEMALE = "FEMALE"  # 女
    OTHER = "OTHER"  # 其他


class EducationEnum(str, Enum):
    """学历枚举（与库中 user_profile.education 对齐）。"""

    HIGH_SCHOOL = "高中"  # 高中
    COLLEGE = "专科"  # 专科
    BACHELOR = "本科"  # 本科
    MASTER = "硕士"  # 硕士
    DOCTOR = "博士"  # 博士
