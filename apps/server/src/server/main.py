"""Server 入口"""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from app.log import configure
from fastapi import FastAPI

from server import routes
from server.core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """应用生命周期"""

    # 环境变量默认值
    os.environ.setdefault("APP_LOG_LEVEL", settings.log_level)
    os.environ.setdefault("APP_LOG_FORMAT", settings.log_format)

    # 初始化日志
    configure()

    yield


# 应用实例
app = FastAPI(title="Server", lifespan=lifespan)

# 注册路由
routes.include_routes(app=app)
