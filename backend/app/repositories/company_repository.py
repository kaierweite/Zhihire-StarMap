"""企业仓储模块。

只做原子数据库操作，不包含业务编排与事务提交。
事务提交由调用方（service 层）负责，仓储仅负责数据访问与刷新以取回主键。
"""
from sqlalchemy import select  # 查询构造
from sqlalchemy.ext.asyncio import AsyncSession  # 异步会话类型

from app.models.entities.company import Company  # 企业 ORM
