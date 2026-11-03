"""外部系统适配 - 工作流客户端装配"""

from app.workflow import WorkflowClient, WorkflowSettings
from app.workflow import create_client as create_workflow_client

from server.core import settings

# ── 工作流 ─────────────────────────

# 客户端装配参数
workflow_settings = WorkflowSettings(
    system_database_url=settings.workflow.system_database_url,
    app_name=settings.workflow.app_name,
)

# 进程级客户端单例
_client: "WorkflowClient | None" = None


def get_workflow_client() -> "WorkflowClient":
    """提交侧 - 工作流客户端单例"""
    global _client

    if _client is None:
        _client = create_workflow_client(workflow_settings)
    return _client
