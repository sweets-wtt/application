"""Server 入口"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from server import routes
from server.core import dependencies


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """应用生命周期"""

    # 装配依赖
    dependencies.setup()

    yield


# 应用实例
app = FastAPI(title="Server", lifespan=lifespan)

# 注册路由
routes.include_routes(app=app)
