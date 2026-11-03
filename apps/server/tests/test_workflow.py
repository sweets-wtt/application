"""工作流服务测试"""

import time
from collections.abc import Iterator
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, cast

import pytest
from app.contracts.generated.http import WorkflowInput
from server import services as workflow_service

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


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
        return SimpleNamespace(status=self.remote_status)


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


async def test_submit_starts_workflow_and_records_idempotency() -> None:
    """首次提交 - 启动工作流并同事务记录幂等键"""
    client = FakeClient()
    session = FakeSession()
    payload = WorkflowInput(message="hi")

    run_id = await workflow_service.submit(
        cast("Any", client), cast("AsyncSession", session), "key-1", payload
    )

    assert run_id == "key-1"
    assert client.started[0][1] == payload
    assert client.started[0][2] == "key-1"
    assert len(session.executed) == 2
    assert session.committed


async def test_submit_returns_existing_on_idempotent_key() -> None:
    """重复幂等键 - 返回已记录 run_id,不启动工作流"""
    existing = SimpleNamespace(run_id="existing-run")
    client = FakeClient()
    session = FakeSession(row=existing)

    run_id = await workflow_service.submit(
        cast("Any", client),
        cast("AsyncSession", session),
        "dup",
        WorkflowInput(message="x"),
    )

    assert run_id == "existing-run"
    assert client.started == []
    assert not session.committed


async def test_get_status_returns_submitted_for_known_run() -> None:
    """已知 run 返回 queued 对应状态"""
    client = FakeClient()
    session = FakeSession(row=SimpleNamespace(run_id="run-1"))

    status = await workflow_service.get_status(
        cast("Any", client), cast("AsyncSession", session), "run-1"
    )

    assert status == "submitted"
    assert client.requested == ["run-1"]


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
    session = FakeSession(row=SimpleNamespace(run_id="run-1"))

    status = await workflow_service.get_status(
        cast("Any", client), cast("AsyncSession", session), "run-1"
    )

    assert status == expected


async def test_get_status_returns_submitted_for_unknown_status() -> None:
    """未知远端状态降级为 submitted"""
    client = FakeClient(status="SOMETHING_NEW")
    session = FakeSession(row=SimpleNamespace(run_id="run-1"))

    status = await workflow_service.get_status(
        cast("Any", client), cast("AsyncSession", session), "run-1"
    )

    assert status == "submitted"


async def test_get_status_returns_submitted_when_query_fails() -> None:
    """查询异常 - 降级为 submitted"""
    client = FakeClient(error=RuntimeError("dbos unavailable"))
    session = FakeSession(row=SimpleNamespace(run_id="run-1"))

    status = await workflow_service.get_status(
        cast("Any", client), cast("AsyncSession", session), "run-1"
    )

    assert status == "submitted"


async def test_get_status_caches_non_terminal_within_ttl() -> None:
    """非终态 TTL 内重复查询 - 只查一次远端"""
    client = FakeClient(status="PENDING")
    session = FakeSession(row=SimpleNamespace(run_id="run-1"))

    first = await workflow_service.get_status(
        cast("Any", client), cast("AsyncSession", session), "run-1"
    )
    second = await workflow_service.get_status(
        cast("Any", client), cast("AsyncSession", session), "run-1"
    )

    assert first == "running"
    assert second == "running"
    assert client.call_count == 1
    assert client.requested == ["run-1"]


async def test_get_status_caches_terminal_status_permanently() -> None:
    """终态结果常驻缓存 - 重复查询不再查远端"""
    client = FakeClient(status="SUCCESS")
    session = FakeSession(row=SimpleNamespace(run_id="run-1"))

    statuses = [
        await workflow_service.get_status(
            cast("Any", client), cast("AsyncSession", session), "run-1"
        )
        for _ in range(3)
    ]

    assert statuses == ["succeeded", "succeeded", "succeeded"]
    assert client.call_count == 1
    assert workflow_service._status_cache["run-1"] == (None, "succeeded")


async def test_get_status_refreshes_non_terminal_after_ttl(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """非终态缓存过期后重新查询"""
    clock = [1000.0]
    monkeypatch.setattr(workflow_service, "monotonic", lambda: clock[0])
    client = FakeClient(status="PENDING")
    session = FakeSession(row=SimpleNamespace(run_id="run-1"))

    first = await workflow_service.get_status(
        cast("Any", client), cast("AsyncSession", session), "run-1"
    )
    second = await workflow_service.get_status(
        cast("Any", client), cast("AsyncSession", session), "run-1"
    )
    assert first == second == "running"
    assert client.call_count == 1

    clock[0] += workflow_service._PENDING_TTL_SECONDS + 1

    third = await workflow_service.get_status(
        cast("Any", client), cast("AsyncSession", session), "run-1"
    )

    assert third == "running"
    assert client.call_count == 2


async def test_get_status_retries_after_failure() -> None:
    """查询异常不写缓存 - 下次请求重试"""
    client = FakeClient(error=RuntimeError("dbos unavailable"))
    session = FakeSession(row=SimpleNamespace(run_id="run-1"))

    first = await workflow_service.get_status(
        cast("Any", client), cast("AsyncSession", session), "run-1"
    )
    assert first == "submitted"
    assert client.call_count == 1
    assert "run-1" not in workflow_service._status_cache

    client.error = None
    client.remote_status = "PENDING"

    second = await workflow_service.get_status(
        cast("Any", client), cast("AsyncSession", session), "run-1"
    )

    assert second == "running"
    assert client.call_count == 2


async def test_get_status_times_out_and_retries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """查询超时 - 降级为 submitted 且下次重试"""
    monkeypatch.setattr(workflow_service, "_QUERY_TIMEOUT_SECONDS", 0.01)
    client = FakeClient(status="PENDING", delay=0.05)
    session = FakeSession(row=SimpleNamespace(run_id="run-1"))

    first = await workflow_service.get_status(
        cast("Any", client), cast("AsyncSession", session), "run-1"
    )
    assert first == "submitted"
    assert client.call_count == 1
    assert "run-1" not in workflow_service._status_cache

    # 恢复超时值 - 线程调度开销可能超过 0.01 秒
    monkeypatch.setattr(workflow_service, "_QUERY_TIMEOUT_SECONDS", 3.0)
    client.delay = 0.0

    second = await workflow_service.get_status(
        cast("Any", client), cast("AsyncSession", session), "run-1"
    )

    assert second == "running"
    assert client.call_count == 2


async def test_get_status_returns_none_for_unknown_run() -> None:
    """未知 run 返回 None, 不查询远端且不写缓存"""
    client = FakeClient()
    session = FakeSession()

    status = await workflow_service.get_status(
        cast("Any", client), cast("AsyncSession", session), "missing"
    )

    assert status is None
    assert client.requested == []
    assert workflow_service._status_cache == {}
