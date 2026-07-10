"""业务异常模块。

定义业务层抛出的可预期异常 `BusinessError`，
携带业务状态码与提示信息，由路由层捕获并封装为统一 `Result` 响应。
"""
from typing import Any  # 任意类型


class BusinessError(Exception):
    """业务可预期异常。

    与运行时不可预期异常区分：本异常携带业务码与提示信息，
    路由层捕获后转换为 `Result.error(code, message)` 而非 500 兜底。

    Attributes:
        code: 业务状态码（非 200）。
        message: 用户可见的提示信息。
        data: 附带数据，默认 None。
    """

    def __init__(self, code: int, message: str, data: Any = None) -> None:
        # 初始化父类异常
        super().__init__(message)
        # 业务状态码
        self.code = code
        # 提示信息
        self.message = message
        # 附带数据
        self.data = data
