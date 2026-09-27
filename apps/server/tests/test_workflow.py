"""工作流服务测试"""

from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, cast

from app.contracts.generated.http import RequestInput
from server.services import workflow as workflow_service

if TYPE_CHECKING:
    from hatchet_sdk import Hatchet
    from sqlalchemy.ext.asyncio import AsyncSession


class FakeRun:
    """工作流 run 引用 - WorkflowRunRef 桩"""

    workflow_run_id = "run-123"


class FakeWorkflow:
    """工作流桩 - 记录触发载荷"""

    def __init__(self) -> None:
        self.payload: Any = None

    async def aio_run_no_wait(self, payload: RequestInput) -> FakeRun:
        self.payload = payload
        return FakeRun()


class FakeClient:
    """Hatchet 客户端桩"""

    def __init__(self) -> None:
        self.workflow_obj = FakeWorkflow()
        self.workflow_name: str | None = None

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
    payload = RequestInput(message="hi")

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
        RequestInput(message="x"),
    )

    assert run_id == "existing-run"
    assert client.workflow_obj.payload is None
    assert not session.committed


async def test_get_status_returns_submitted_for_known_run() -> None:
    """已知 run 返回 submitted"""
    session = FakeSession(row=SimpleNamespace(run_id="run-1"))

    status = await workflow_service.get_status(cast("AsyncSession", session), "run-1")

    assert status == "submitted"


async def test_get_status_returns_none_for_unknown_run() -> None:
    """未知 run 返回 None"""
    session = FakeSession()

    status = await workflow_service.get_status(cast("AsyncSession", session), "missing")

    assert status is None
