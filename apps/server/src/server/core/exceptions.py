"""应用异常"""

from fastapi import Request
from fastapi.responses import JSONResponse


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


async def handle_app_error(request: Request, exc: Exception) -> JSONResponse:
    """业务异常响应 - 统一错误结构"""
    # 业务异常 - 使用自定义状态码与描述
    if isinstance(exc, AppError):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    # 非业务异常 - 回退内部错误
    return JSONResponse(status_code=500, content={"detail": "内部错误"})
