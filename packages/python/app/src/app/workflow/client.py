from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True)
class WorkflowSettings:
    """工作流装配参数"""

    token: str
    server_url: str

    @classmethod
    def from_env(cls) -> Self:
        """从环境变量装配"""
        return cls(
            token=os.environ["APP_WORKFLOW_TOKEN"],
            server_url=os.environ.get("APP_WORKFLOW_SERVER_URL", ""),
        )


def create_client[T](settings: WorkflowSettings, client_factory: Callable[..., T]) -> T:
    """创建工作流客户端"""
    return client_factory(token=settings.token, server_url=settings.server_url)
