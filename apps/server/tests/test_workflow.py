"""工作流服务测试"""

import time
from collections.abc import Iterator
from typing import Any, cast

import pytest
from app.contracts.generated.http import WorkflowInput
from server import services as workflow_service


@pytest.fixture(autouse=True)
def _clear_status_cache() -> Iterator[None]:
    """清空进程级状态缓存, 避免用例间污染"""
    workflow_service._status_cache.clear()
    yield
    workflow_service._status_cache.clear()


class FakeClient:
    """工作流客户端桩 - 记录启动参数, 返回固定状态或抛出异常"""

    def __init__(
        self,
        status: Any = "ENQUEUED",
        error: Exception | None = None,
        delay: float = 0.0,
    ) -> None:
        # 内部字段避开 status 方法名 - status 是查询入口
        self.remote_status = status
        self.error = error
        self.delay = delay
        self.started: list[tuple[Any, Any, str]] = []
        self.requested: list[str] = []

    @property
    def call_count(self) -> int:
        """状态查询次数"""
        return len(self.requested)

    def start(self, workflow: Any, payload: Any, workflow_id: str) -> str:
        """启动工作流 - 返回幂等键作为 run_id"""
        self.started.append((workflow, payload, workflow_id))
        return workflow_id

    def status(self, run_id: str) -> Any:
        """状态查询入口 - 与 DBOS 同步接口对齐"""
        self.requested.append(run_id)
        if self.delay:
            time.sleep(self.delay)
        if self.error is not None:
            raise self.error
        return self.remote_status


async def test_submit_starts_workflow_with_idempotency_key() -> None:
    """提交 - 以幂等键为 workflow_id 启动"""
    client = FakeClient()
    payload = WorkflowInput(message="hi")

    run_id = await workflow_service.submit(cast("Any", client), "key-1", payload)

    assert run_id == "key-1"
    assert client.started[0][1] == payload
    assert client.started[0][2] == "key-1"


async def test_get_status_returns_none_for_unknown_run() -> None:
    """远端无此 run - 返回 None"""
    client = FakeClient(status=None)

    status = await workflow_service.get_status(cast("Any", client), "missing")

    assert status is None


@pytest.mark.parametrize(
    ("remote", "expected"),
    [
        ("ENQUEUED", "submitted"),
        ("DELAYED", "submitted"),
        ("PENDING", "running"),
        ("SUCCESS", "succeeded"),
        ("ERROR", "failed"),
        ("MAX_RECOVERY_ATTEMPTS_EXCEEDED", "failed"),
        ("CANCELLED", "failed"),
    ],
    ids=[
        "enqueued",
        "delayed",
        "pending",
        "success",
        "error",
        "recovery-exceeded",
        "cancelled",
    ],
)
async def test_get_status_maps_dbos_status(remote: str, expected: str) -> None:
    """DBOS 状态映射到契约枚举"""
    client = FakeClient(status=remote)

    status = await workflow_service.get_status(cast("Any", client), "run-1")

    assert status == expected


async def test_get_status_returns_submitted_for_unknown_status() -> None:
    """未知远端状态降级为 submitted"""
    client = FakeClient(status="SOMETHING_NEW")

    status = await workflow_service.get_status(cast("Any", client), "run-1")

    assert status == "submitted"


async def test_get_status_returns_submitted_when_query_fails() -> None:
    """查询异常 - 降级为 submitted"""
    client = FakeClient(error=RuntimeError("dbos unavailable"))

    status = await workflow_service.get_status(cast("Any", client), "run-1")

    assert status == "submitted"


async def test_get_status_caches_non_terminal_within_ttl() -> None:
    """非终态 TTL 内重复查询 - 只查一次远端"""
    client = FakeClient(status="PENDING")

    first = await workflow_service.get_status(cast("Any", client), "run-1")
    second = await workflow_service.get_status(cast("Any", client), "run-1")

    assert first == "running"
    assert second == "running"
    assert client.call_count == 1
    assert client.requested == ["run-1"]
