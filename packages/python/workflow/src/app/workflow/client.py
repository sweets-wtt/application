"""工作流客户端"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self

from dbos import DBOS, DBOSConfig, SetWorkflowID
from sqlalchemy.pool import NullPool


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
        is_sqlite = self._settings.system_database_url.startswith("sqlite")

        config: DBOSConfig = {
            "name": self._settings.app_name,
            "system_database_url": self._settings.system_database_url,
            # 执行器标识 - 重启时只恢复同标识的未完成工作流
            # 取容器主机名而非进程标识, 多 worker 共享同一标识,
            # 否则 worker 重启后其旧任务无人认领而永久滞留
            "executor_id": self._executor_id(),
        }

        if is_sqlite:
            # SQLite 不接受连接池参数, 换用 NullPool 由 DBOS 剥离
            # 此时也不能设 sys_db_pool_size, DBOS 会把它转成 pool_size 传入而报错
            config["db_engine_kwargs"] = {"poolclass": NullPool}
        else:
            # 系统库连接池 - 默认 20 对低频控制面操作过剩, 压低以留出应用侧余量
            config["sys_db_pool_size"] = 5

        DBOS(config=config)
        DBOS.launch()

    @staticmethod
    def _executor_id() -> str:
        """执行器标识 - 显式配置优先, 否则取容器主机名"""
        return os.environ.get("DBOS__VMID") or os.environ.get("HOSTNAME") or "local"

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
