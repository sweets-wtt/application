"""应用异常"""

import typing

from fastapi.responses import JSONResponse


if typing.TYPE_CHECKING:
    from fastapi import Request


class AppError(Exception):
    """业务异常基类"""

    # 响应状态码
    status_code: int = 500

    # 错误描述
    detail: str = "内部错误"

    def __init__(self, detail: str | None = None) -> None:
        """初始化业务异常"""
        if detail is not None:
            self.detail = detail


def handle_app_error(_request: Request, exc: Exception) -> JSONResponse:
    """业务异常响应 - 统一错误结构

    Args:
        _request: 请求对象（未使用）
        exc: 捕获到的异常

    Returns:
        JSONResponse: 统一格式的错误响应
    """
    # 业务异常 - 使用自定义状态码与描述
    if isinstance(exc, AppError):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    # 非业务异常 - 复用基类默认值
    fallback = AppError()
    return JSONResponse(status_code=fallback.status_code, content={"detail": fallback.detail})
