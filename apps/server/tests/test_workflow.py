"""工作流服务测试"""

import asyncio
from collections.abc import Iterator
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, cast

import pytest
from app.contracts.generated.http import WorkflowInput
from server.services import workflow as workflow_service

if TYPE_CHECKING:
    from hatchet_sdk import Hatchet
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(autouse=True)
def _clear_status_cache() -> Iterator[None]:
    """清空进程级状态缓存, 避免用例间污染"""
    workflow_service._status_cache.clear()
    yield
    workflow_service._status_cache.clear()


class FakeRun:
    """工作流 run 引用 - WorkflowRunRef 桩"""

    workflow_run_id = "run-123"


class FakeWorkflow:
    """工作流桩 - 记录触发载荷"""

    def __init__(self) -> None:
        self.payload: Any = None

    async def aio_run_no_wait(self, payload: WorkflowInput) -> FakeRun:
        self.payload = payload
        return FakeRun()


class FakeRuns:
    """runs 客户端桩 - 返回固定状态或抛出异常"""

    def __init__(
        self,
        status: Any = "QUEUED",
        error: Exception | None = None,
        delay: float = 0.0,
    ) -> None:
        self.status = status
        self.error = error
        self.delay = delay
        self.requested: list[str] = []

    @property
    def call_count(self) -> int:
        """RPC 调用次数"""
        return len(self.requested)

    async def aio_get_status(self, run_id: str) -> Any:
        self.requested.append(run_id)
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.error is not None:
            raise self.error
        return self.status


class FakeClient:
    """Hatchet 客户端桩"""

    def __init__(
        self,
        status: Any = "QUEUED",
        error: Exception | None = None,
        delay: float = 0.0,
    ) -> None:
        self.workflow_obj = FakeWorkflow()
        self.workflow_name: str | None = None
        self.runs = FakeRuns(status=status, error=error, delay=delay)

    def workflow(self, **kwargs: Any) -> FakeWorkflow:
        self.workflow_name = kwargs.get("name")
        return self.workflow_obj


class FakeResult:
    """查询结果桩"""

    def __init__(self, row: Any = None) -> None:
        self._row = row

    def first(self) -> Any:
        return self._row


class FakeSession:
    """数据库会话桩"""

    def __init__(self, row: Any = None) -> None:
        self._row = row
        self.executed: list[tuple[Any, Any]] = []
        self.committed = False

    async def execute(self, stmt: Any, params: Any = None) -> FakeResult:
        self.executed.append((stmt, params))
        return FakeResult(self._row)

    async def commit(self) -> None:
        self.committed = True


async def test_submit_triggers_run_and_records_idempotency() -> None:
    """首次提交 - 触发 run 并同事务记录幂等键"""
    client = FakeClient()
    session = FakeSession()
    payload = WorkflowInput(message="hi")

    run_id = await workflow_service.submit(
        cast("Hatchet", client), cast("AsyncSession", session), "key-1", payload
    )

    assert run_id == "run-123"
    assert client.workflow_name == "request"
    assert client.workflow_obj.payload == payload
    assert len(session.executed) == 2
    assert session.committed


async def test_submit_returns_existing_on_idempotent_key() -> None:
    """重复幂等键 - 返回已记录 run_id,不触发 run"""
    existing = SimpleNamespace(run_id="existing-run")
    client = FakeClient()
    session = FakeSession(row=existing)

    run_id = await workflow_service.submit(
        cast("Hatchet", client),
        cast("AsyncSession", session),
        "dup",
        WorkflowInput(message="x"),
    )

    assert run_id == "existing-run"
    assert client.workflow_obj.payload is None
    assert not session.committed


async def test_get_status_returns_submitted_for_known_run() -> None:
    """已知 run 返回 submitted"""
    client = FakeClient()
    session = FakeSession(row=SimpleNamespace(run_id="run-1"))

    status = await workflow_service.get_status(
        cast("Hatchet", client), cast("AsyncSession", session), "run-1"
    )

    assert status == "submitted"
    assert client.runs.requested == ["run-1"]


@pytest.mark.parametrize(
    ("remote", "expected"),
    [
        (SimpleNamespace(value="QUEUED"), "submitted"),
        (SimpleNamespace(value="RUNNING"), "running"),
        (SimpleNamespace(value="COMPLETED"), "succeeded"),
        (SimpleNamespace(value="FAILED"), "failed"),
        (SimpleNamespace(value="CANCELLED"), "failed"),
    ],
    ids=["queued", "running", "completed", "failed", "cancelled"],
)
async def test_get_status_maps_hatchet_status(remote: Any, expected: str) -> None:
    """Hatchet 状态映射到契约枚举"""
    client = FakeClient(status=remote)
    session = FakeSession(row=SimpleNamespace(run_id="run-1"))

    status = await workflow_service.get_status(
        cast("Hatchet", client), cast("AsyncSession", session), "run-1"
    )

    assert status == expected


async def test_get_status_maps_plain_string_status() -> None:
    """Hatchet 返回纯字符串状态时同样映射"""
    client = FakeClient(status="COMPLETED")
    session = FakeSession(row=SimpleNamespace(run_id="run-1"))

    status = await workflow_service.get_status(
        cast("Hatchet", client), cast("AsyncSession", session), "run-1"
    )

    assert status == "succeeded"


async def test_get_status_returns_submitted_for_unknown_status() -> None:
    """未知远端状态降级为 submitted"""
    client = FakeClient(status=SimpleNamespace(value="SOMETHING_NEW"))
    session = FakeSession(row=SimpleNamespace(run_id="run-1"))

    status = await workflow_service.get_status(
        cast("Hatchet", client), cast("AsyncSession", session), "run-1"
    )

    assert status == "submitted"


async def test_get_status_returns_submitted_when_hatchet_fails() -> None:
    """Hatchet 查询异常 - 降级为 submitted"""
    client = FakeClient(error=RuntimeError("hatchet unavailable"))
    session = FakeSession(row=SimpleNamespace(run_id="run-1"))

    status = await workflow_service.get_status(
        cast("Hatchet", client), cast("AsyncSession", session), "run-1"
    )

    assert status == "submitted"


async def test_get_status_caches_non_terminal_within_ttl() -> None:
    """非终态 TTL 内重复查询 - 只打一次 RPC"""
    client = FakeClient(status=SimpleNamespace(value="RUNNING"))
    session = FakeSession(row=SimpleNamespace(run_id="run-1"))

    first = await workflow_service.get_status(
        cast("Hatchet", client), cast("AsyncSession", session), "run-1"
    )
    second = await workflow_service.get_status(
        cast("Hatchet", client), cast("AsyncSession", session), "run-1"
    )

    assert first == "running"
    assert second == "running"
    assert client.runs.call_count == 1
    assert client.runs.requested == ["run-1"]


async def test_get_status_caches_terminal_status_permanently() -> None:
    """终态结果常驻缓存 - 重复查询不再打 RPC"""
    client = FakeClient(status=SimpleNamespace(value="COMPLETED"))
    session = FakeSession(row=SimpleNamespace(run_id="run-1"))

    statuses = [
        await workflow_service.get_status(
            cast("Hatchet", client), cast("AsyncSession", session), "run-1"
        )
        for _ in range(3)
    ]

    assert statuses == ["succeeded", "succeeded", "succeeded"]
    assert client.runs.call_count == 1
    assert workflow_service._status_cache["run-1"] == (None, "succeeded")


async def test_get_status_refreshes_non_terminal_after_ttl(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """非终态缓存过期后重新查询"""
    clock = [1000.0]
    monkeypatch.setattr(workflow_service, "monotonic", lambda: clock[0])
    client = FakeClient(status=SimpleNamespace(value="RUNNING"))
    session = FakeSession(row=SimpleNamespace(run_id="run-1"))

    first = await workflow_service.get_status(
        cast("Hatchet", client), cast("AsyncSession", session), "run-1"
    )
    second = await workflow_service.get_status(
        cast("Hatchet", client), cast("AsyncSession", session), "run-1"
    )
    assert first == second == "running"
    assert client.runs.call_count == 1

    clock[0] += workflow_service._PENDING_TTL_SECONDS + 1

    third = await workflow_service.get_status(
        cast("Hatchet", client), cast("AsyncSession", session), "run-1"
    )

    assert third == "running"
    assert client.runs.call_count == 2


async def test_get_status_retries_rpc_after_failure() -> None:
    """查询异常不写缓存 - 下次请求重试 RPC"""
    client = FakeClient(error=RuntimeError("hatchet unavailable"))
    session = FakeSession(row=SimpleNamespace(run_id="run-1"))

    first = await workflow_service.get_status(
        cast("Hatchet", client), cast("AsyncSession", session), "run-1"
    )
    assert first == "submitted"
    assert client.runs.call_count == 1
    assert "run-1" not in workflow_service._status_cache

    client.runs.error = None
    client.runs.status = SimpleNamespace(value="RUNNING")

    second = await workflow_service.get_status(
        cast("Hatchet", client), cast("AsyncSession", session), "run-1"
    )

    assert second == "running"
    assert client.runs.call_count == 2


async def test_get_status_times_out_and_retries_rpc(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """查询超时 - 降级为 submitted 且下次重试 RPC"""
    monkeypatch.setattr(workflow_service, "_QUERY_TIMEOUT_SECONDS", 0.01)
    client = FakeClient(status=SimpleNamespace(value="RUNNING"), delay=0.05)
    session = FakeSession(row=SimpleNamespace(run_id="run-1"))

    first = await workflow_service.get_status(
        cast("Hatchet", client), cast("AsyncSession", session), "run-1"
    )
    assert first == "submitted"
    assert client.runs.call_count == 1
    assert "run-1" not in workflow_service._status_cache

    client.runs.delay = 0.0

    second = await workflow_service.get_status(
        cast("Hatchet", client), cast("AsyncSession", session), "run-1"
    )

    assert second == "running"
    assert client.runs.call_count == 2


async def test_get_status_returns_none_for_unknown_run() -> None:
    """未知 run 返回 None, 不查询 Hatchet 且不写缓存"""
    client = FakeClient()
    session = FakeSession()

    status = await workflow_service.get_status(
        cast("Hatchet", client), cast("AsyncSession", session), "missing"
    )

    assert status is None
    assert client.runs.requested == []
    assert workflow_service._status_cache == {}
