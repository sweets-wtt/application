"""Server 入口"""

from contextlib import asynccontextmanager

import fastapi

from server import routes, services
from server.adapters import bus, get_workflow_client
from server.core import setup

# 装配依赖 - 须先于应用实例化以替换 FastAPI 类
setup()


@asynccontextmanager
async def lifespan(_: fastapi.FastAPI):
    """应用生命周期 - 启动/关闭实时总线与工作流"""

    async def on_message(topic: str, message: str) -> None:
        """总线消息转发至 Hub 对应主题"""
        await services.hub.broadcast_to(topic, message)

    # 工作流在应用启动前拉起 - 进程内仅一次
    workflow_client = get_workflow_client()
    workflow_client.launch()

    await bus.start(on_message)

    try:
        yield
    finally:
        await bus.close()


# 应用实例 - 经替换后的类自动埋点
app = fastapi.FastAPI(title="Server", lifespan=lifespan)

# 注册路由
routes.include_routes(app=app)
