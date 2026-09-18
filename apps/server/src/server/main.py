"""Server 入口"""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from app.log import get_logger
from fastapi import FastAPI

from server import routes
from server.core.dependencies import setup_telemetry, shutdown_telemetry
from server.core.settings import settings

# 日志器
log = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """应用生命周期"""

    # 环境变量默认值
    os.environ.setdefault("APP_LOG_LEVEL", settings.log_level)
    os.environ.setdefault("APP_LOG_FORMAT", settings.log_format)

    # 一次装配 日志 OTLP 与 FastAPI instrumentation
    setup_telemetry(app)

    # 启动日志 api 服务 OTLP 日志数据源
    log.info("startup")

    yield

    log.info("shutdown")

    # 冲刷并关闭遥测资源
    shutdown_telemetry()


# 应用实例
app = FastAPI(title="Server", lifespan=lifespan)

# 注册路由
routes.include_routes(app=app)
