"""FastAPI 应用入口。

负责应用实例的创建与全局组件装配：
- CORS 中间件配置
- 路由挂载（统一挂载到 `/api` 前缀下）
- 全局异常处理（422 校验、HTTP 异常、运行时异常统一封装为 Result）
"""
import asyncio  # 事件循环（用于 Windows 策略）
import sys  # 平台检测

# Windows 上 psycopg async 需要 SelectorEventLoop 而非 ProactorEventLoop
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# KingbaseES 兼容性补丁：在引擎创建前修补 SQLAlchemy PG dialect
from app.db import compat  # noqa: F401

from fastapi import FastAPI, HTTPException, Request  # 应用实例与异常类型
from fastapi.exceptions import RequestValidationError  # 请求参数校验异常
from fastapi.middleware.cors import CORSMiddleware  # CORS 中间件
from fastapi.responses import JSONResponse  # 自定义响应

from app.api.v1 import api_router  # v1 路由聚合器
from app.config.settings import settings  # 全局配置
from app.models.schemas.result import Result  # 统一响应模型
from app.db.session import async_engine  # 异步引擎（确保 session 已知晓 patch）


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例。

    Returns:
        FastAPI: 已装配中间件、路由与异常处理器的应用实例。
    """
    # 创建应用实例，设置标题、版本与描述
    app = FastAPI(
        title=settings.app_name,  # 应用标题：智聘星图
        version="0.1.0",  # 当前后端版本
        description="基于银河麒麟操作系统的 AI 智能匹配与能力图谱平台后端",
        docs_url=f"{settings.api_prefix}/docs",  # OpenAPI 文档地址
        redoc_url=f"{settings.api_prefix}/redoc",  # ReDoc 文档地址
        lifespan=_lifespan,  # 生命周期管理：优雅关闭数据库连接池
    )

    # ===== CORS 跨域中间件：允许前端开发环境来源 =====
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,  # 允许的前端来源
        allow_credentials=True,  # 允许携带 Cookie
        allow_methods=["*"],  # 允许所有方法
        allow_headers=["*"],  # 允许所有请求头
    )

    # ===== 路由挂载：统一加上 `/api` 前缀 =====
    app.include_router(api_router, prefix=settings.api_prefix)

    # ===== 全局异常处理器：统一封装响应 =====
    register_exception_handlers(app)

    return app


async def _lifespan(app: FastAPI):
    """应用生命周期管理。

    在应用启动时初始化资源，在关闭时释放数据库连接池，
    防止连接泄漏导致数据库连接数耗尽。

    Args:
        app: FastAPI 应用实例。

    Yields:
        None: 启动完成后进入运行状态。
    """
    yield
    await async_engine.dispose()


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器。

    将参数校验异常(422)、HTTP 异常与其他未捕获的运行时异常统一封装为 `Result` 结构，
    保证前端始终能在 data 字段约定上做成功/失败判定。

    Args:
        app: FastAPI 应用实例。
    """

    @app.exception_handler(RequestValidationError)
    async def _validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """将请求参数校验异常统一封装为 Result 结构。

        Args:
            request: 当前请求。
            exc: 校验异常，携带字段级错误列表。

        Returns:
            JSONResponse: code=422 的统一错误响应，data 为字段级错误明细。
        """
        # 构造可序列化的字段级错误明细，剔除 ctx 中的非 JSON 原生对象（如 ValueError）
        details = [
            {"loc": e.get("loc"), "msg": e.get("msg"), "type": e.get("type")}
            for e in exc.errors()
        ]
        # 封装为统一 Result，附带字段级错误明细
        result = Result.error(code=422, message="请求参数校验失败", data=details)
        return JSONResponse(status_code=422, content=result.model_dump())

    @app.exception_handler(HTTPException)
    async def _http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """将 HTTP 异常统一封装为 Result 结构。

        Args:
            request: 当前请求。
            exc: HTTP 异常实例。

        Returns:
            JSONResponse: 以 HTTP 异常状态码封装的统一错误响应。
        """
        # detail 可能为字符串或列表，统一取字符串提示
        detail = exc.detail if isinstance(exc.detail, str) else "请求异常"
        # 封装为统一 Result
        result = Result.error(code=exc.status_code, message=detail, data=None)
        return JSONResponse(status_code=exc.status_code, content=result.model_dump())

    @app.exception_handler(Exception)
    async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """处理未捕获的运行时异常。

        Args:
            request: 当前请求。
            exc: 抛出的异常实例。

        Returns:
            JSONResponse: code=500 的统一错误响应。
        """
        # 构造兜底错误响应，避免泄漏内部堆栈到前端
        result = Result.error(code=500, message="服务器内部错误", data=None)
        return JSONResponse(status_code=500, content=result.model_dump())


# 应用实例：uvicorn 通过 `app.main:app` 引用
app = create_app()
