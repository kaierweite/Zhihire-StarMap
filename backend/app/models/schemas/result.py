"""统一响应模型模块。

所有 API 返回统一封装为 `Result[T]`：`{ code, message, data }`，
保证前端拥有一致的成功/失败判定逻辑。
"""
from typing import Any, Generic, TypeVar  # 泛型支持与任意类型

from pydantic import BaseModel, ConfigDict  # 模型基类与配置


# 响应数据的泛型类型变量
T = TypeVar("T")


class ResultModel(BaseModel, Generic[T]):
    """统一响应模型。

    通过泛型 `Result[T]` 声明 data 的具体类型，
    兼顾 OpenAPI 文档的可读性与运行时校验。

    Attributes:
        code: 业务状态码，200 表示成功，其余为失败/异常码。
        message: 提示信息，成功为 "success"，失败为具体原因。
        data: 业务数据，失败或无数据时为 None。
    """

    # 允许从 ORM / 属性对象构造，并放宽类型限制以容纳任意业务模型
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    code: int = 200  # 默认成功状态码
    message: str = "success"  # 默认成功提示
    data: T | None = None  # 默认无业务数据

    @staticmethod
    def success(data: Any = None, message: str = "success") -> "ResultModel[Any]":
        """构建成功响应。

        Args:
            data: 业务数据，默认为 None。
            message: 提示信息，默认 "success"。

        Returns:
            ResultModel[Any]: code=200 的成功响应。
        """
        # 拼装成功响应：状态码固定 200
        return ResultModel[Any](code=200, message=message, data=data)

    @staticmethod
    def error(code: int, message: str, data: Any = None) -> "ResultModel[Any]":
        """构建失败响应。

        Args:
            code: 业务错误码（非 200）。
            message: 错误提示信息。
            data: 附带数据，默认为 None。

        Returns:
            ResultModel[Any]: 指定错误码的失败响应。
        """
        # 拼装失败响应，data 可携带额外上下文供前端提示
        return ResultModel[Any](code=code, message=message, data=data)


# 对外通用别名：业务代码统一使用 `Result`
Result = ResultModel


class PageResult(BaseModel):
    """分页响应模型。

    用于列表类接口的分页封装：`{ records, total, page, size }`。

    Attributes:
        records: 当前页的记录列表。
        total: 总记录数。
        page: 当前页码（从 1 开始）。
        size: 每页条数。
    """

    records: list[Any] = []  # 当前页记录，默认空列表
    total: int = 0  # 总记录数
    page: int = 1  # 当前页码
    size: int = 20  # 每页条数