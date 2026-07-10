"""业务服务层包。

集中导出业务异常与各业务服务模块，供路由层按需调用。
"""
from app.services import company_service  # day10 企业业务
from app.services import admin_service  # day11 管理员后台
from app.services.errors import BusinessError  # 业务异常

__all__ = [
    "BusinessError",
    "company_service",
    "admin_service",
]
