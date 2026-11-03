"""Server 入口"""

from contextlib import asynccontextmanager

import fastapi
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from server import routes
from server.adapters import get_workflow_client
from server.core import setup
from server.limits import limiter

# 装配依赖 - 初始化日志等, 须先于应用实例化
setup()


@asynccontextmanager
async def lifespan(_: fastapi.FastAPI):
    """应用生命周期 - 启动前拉起工作流

    工作流在应用启动前拉起 - 进程内仅一次
    """
    workflow_client = get_workflow_client()
    workflow_client.launch()

    yield


# 应用实例
app = fastapi.FastAPI(title="Server", lifespan=lifespan)

# 限流 - 状态挂到应用供装饰器解析, 超限统一返回 429


def on_rate_limit_exceeded(request: Request, exc: Exception) -> JSONResponse:
    """超限响应 - 与契约错误结构对齐"""
    detail = "请求过于频繁"
    if isinstance(exc, RateLimitExceeded):
        detail = f"请求过于频繁: {exc.limit}"

    return JSONResponse(status_code=429, content={"detail": detail})


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, on_rate_limit_exceeded)

# 注册路由
routes.include_routes(app=app)
