"""
智聘星图 AI 微服务 — 启动入口
lifespan 钩子中完成 DB 连接池 + LLM 客户端 + 图谱重建
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.exceptions import register_exception_handlers
from app.api.health import router as health_router
from app.api.parse import router as parse_router
from app.api.graph import router as graph_router
from app.api.recommend import router as recommend_router
from app.api.career import router as career_router
from app.api.interview import router as interview_router
from app.api.resume_optimize import router as resume_opt_router
from app.infrastructure.llm_client import llm_client
from app.infrastructure.db_client import db_client
from app.core.graph.skill_graph import skill_graph

logger = logging.getLogger("zhihire.ai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动/关闭钩子"""
    logger.info("AI 服务启动中...")

    # 初始化 LLM 客户端
    await llm_client.init()
    logger.info("LLM 客户端已初始化")

    # 初始化数据库连接池（可选，DB 不可用时图谱为空）
    try:
        await db_client.init()
        logger.info("数据库连接池已初始化")

        # 从 DB 全量重建内存图
        skills = await db_client.fetch_skills()
        relations = await db_client.fetch_relations()
        skill_graph.rebuild(skills, relations)
        logger.info(
            f"图谱已重建: {skill_graph.get_node_count()} 节点, "
            f"{skill_graph.get_edge_count()} 条边"
        )
    except Exception as e:
        logger.warning(f"数据库不可用，图谱为空: {e}")

    yield

    # 关闭资源
    await llm_client.close()
    await db_client.close()
    logger.info("AI 服务已停止")


app = FastAPI(
    title="智聘星图 AI 微服务",
    description="简历解析 · 技能图谱 · 匹配评分 · 职业规划 · 模拟面试",
    version="1.0.0",
    lifespan=lifespan,
)

# 注册全局异常处理
register_exception_handlers(app)

# 挂载路由
app.include_router(health_router)
app.include_router(parse_router)
app.include_router(graph_router)
app.include_router(recommend_router)
app.include_router(career_router)
app.include_router(interview_router)
app.include_router(resume_opt_router)


if __name__ == "__main__":
    import uvicorn
    from app.infrastructure.config_manager import settings

    uvicorn.run(
        "main:app",
        host=settings.ai_service_host,
        port=settings.ai_service_port,
        workers=1,
        reload=True,
    )
