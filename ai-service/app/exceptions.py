"""
自定义异常模块
定义 AI 服务的业务异常和全局异常处理器
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AIServiceException(Exception):
    """AI 服务基础异常"""

    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code


class LLMCallError(AIServiceException):
    """LLM 调用失败"""

    def __init__(self, message: str = "LLM 调用失败"):
        super().__init__(code="LLM_CALL_ERROR", message=message, status_code=502)


class DocumentParseError(AIServiceException):
    """文档解析失败"""

    def __init__(self, message: str = "文档解析失败"):
        super().__init__(code="DOC_PARSE_ERROR", message=message, status_code=422)


class GraphBuildError(AIServiceException):
    """图谱构建失败"""

    def __init__(self, message: str = "图谱构建失败"):
        super().__init__(code="GRAPH_BUILD_ERROR", message=message, status_code=500)


class FileReadError(AIServiceException):
    """文件读取失败"""

    def __init__(self, message: str = "文件读取失败"):
        super().__init__(code="FILE_READ_ERROR", message=message, status_code=404)


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器"""

    @app.exception_handler(AIServiceException)
    async def ai_service_exception_handler(
        request: Request, exc: AIServiceException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.code,
                "message": exc.message,
                "data": None,
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        # 未预期异常，返回 500
        return JSONResponse(
            status_code=500,
            content={
                "code": "INTERNAL_ERROR",
                "message": str(exc),
                "data": None,
            },
        )
