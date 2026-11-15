"""Server 入口"""

from contextlib import asynccontextmanager

import fastapi

from server import routes
from server.adapters.realtime import bus
from server.core import dependencies
from server.services import realtime as realtime_service

# 装配依赖 - 须先于应用实例化以替换 FastAPI 类
dependencies.setup()


@asynccontextmanager
async def lifespan(_: fastapi.FastAPI):
    """应用生命周期 - 启动/关闭实时总线"""

    async def on_message(topic: str, message: str) -> None:
        """总线消息转发到 Hub 对应主题"""
        await realtime_service.hub.broadcast_to(topic, message)

    await bus.start(on_message)

    try:
        yield
    finally:
        await bus.close()


# 应用实例 - 经替换后的类自动埋点
app = fastapi.FastAPI(title="Server", lifespan=lifespan)

# 注册路由
routes.include_routes(app=app)
