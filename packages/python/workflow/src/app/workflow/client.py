"""工作流客户端"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self

from dbos import DBOS, DBOSConfig, SetWorkflowID


@dataclass(frozen=True)
class WorkflowSettings:
    """工作流装配参数"""

    # 系统库连接串 - 工作流与步骤状态落库
    system_database_url: str

    # 应用名 - 同一系统库内区分应用归属
    app_name: str = "application"

    @classmethod
    def from_env(cls) -> Self:
        """从环境变量装配"""
        return cls(
            system_database_url=os.environ["APP_WORKFLOW_SYSTEM_DATABASE_URL"],
        )


class WorkflowClient:
    """DBOS 工作流客户端 - 封装启动与状态查询

    薄封装便于测试注入, 运行时行为完全由 DBOS 提供
    """

    def __init__(self, settings: WorkflowSettings) -> None:
        self._settings = settings

    def launch(self) -> None:
        """初始化并启动 DBOS - 进程内仅调用一次"""
        self._ensure_sqlite_dir()
        config: DBOSConfig = {
            "name": self._settings.app_name,
            "system_database_url": self._settings.system_database_url,
        }
        DBOS(config=config)
        DBOS.launch()

    def _ensure_sqlite_dir(self) -> None:
        """SQLite 系统库的父目录不存在时创建

        DBOS 不会自动建目录, 缺目录会以 unable to open database file 失败
        """
        url = self._settings.system_database_url
        prefix = "sqlite:///"
        if not url.startswith(prefix):
            return

        path = url[len(prefix) :]
        if not path or path == ":memory:":
            return

        parent = Path(path).parent
        if str(parent) not in {"", "."}:
            parent.mkdir(parents=True, exist_ok=True)

    def start(self, workflow: Any, payload: Any, workflow_id: str) -> str:
        """以幂等键为 workflow_id 启动工作流 - 同键不会重复执行"""
        with SetWorkflowID(workflow_id):
            handle = DBOS.start_workflow(workflow, payload)

        return handle.get_workflow_id()

    def status(self, run_id: str) -> Any:
        """查询远端状态 - 不存在返回 None"""
        return DBOS.get_workflow_status(run_id)


def create_client(settings: WorkflowSettings) -> WorkflowClient:
    """创建工作流客户端"""
    return WorkflowClient(settings)
