"""工作流适配器"""

from typing import TYPE_CHECKING

from app.workflow import WorkflowSettings, create_client

from server.core.settings import settings

if TYPE_CHECKING:
    from hatchet_sdk import Hatchet

# 客户端装配参数
client_settings = WorkflowSettings(
    token=settings.workflow.token,
    server_url=settings.workflow.server_url,
)

# 进程级客户端单例
_client: "Hatchet | None" = None


def get_client() -> "Hatchet":
    """提交侧 - Hatchet 客户端单例"""
    global _client

    if _client is None:
        _client = create_client(client_settings)
    return _client


def build_worker():
    """执行侧 - 创建 worker

    worker.start() 阻塞且禁止在已有 asyncio 循环内调用
    """
    # 惰性导入避免循环依赖、执行侧才装配工作流
    from server.workflows.request import workflow

    return get_client().worker(name="server-worker", workflows=[workflow])
