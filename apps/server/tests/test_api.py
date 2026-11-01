"""契约模糊测试"""

from collections.abc import AsyncIterator
from types import SimpleNamespace
from typing import Any

import schemathesis
from schemathesis.specs.openapi.checks import (
    allow_header_conformance,
    negative_data_rejection,
    unsupported_method,
)
from server.adapters.database import get_session
from server.adapters.realtime import get_ticket_store
from server.adapters.storage import get_client as get_storage_client
from server.adapters.workflow import get_client
from server.main import app

# 契约单一来源 - 直接加载契约文件
schema = schemathesis.openapi.from_path("contracts/http/openapi.yaml")


# 离线桩 - 外部依赖(Hatchet/数据库/对象存储/票据存储)在测试环境不可用,
# 模糊测试只验证契约符合性
class _FakeRun:
    """工作流 run 引用桩"""

    workflow_run_id = "run-test"


class _FakeWorkflow:
    """工作流桩"""

    async def aio_run_no_wait(self, _payload: object) -> _FakeRun:
        return _FakeRun()


class _FakeRuns:
    """runs 客户端桩 - 固定返回 COMPLETED"""

    async def aio_get_status(self, _run_id: str) -> SimpleNamespace:
        return SimpleNamespace(value="COMPLETED")


class _FakeClient:
    """Hatchet 客户端桩"""

    def __init__(self) -> None:
        self.runs = _FakeRuns()

    def workflow(self, **_kwargs: object) -> _FakeWorkflow:
        return _FakeWorkflow()


class _FakeResult:
    """查询结果桩"""

    def first(self) -> None:
        return None


class _FakeSession:
    """数据库会话桩"""

    async def execute(self, _stmt: object, _params: object = None) -> _FakeResult:
        return _FakeResult()

    async def commit(self) -> None:
        pass


class _FakeBody:
    """对象内容桩"""

    async def iter_chunks(self) -> AsyncIterator[bytes]:
        yield b"payload"


class _FakeStorage:
    """对象存储客户端桩"""

    async def put_object(self, **_kwargs: Any) -> dict[str, Any]:
        return {}

    async def get_object(self, **_kwargs: Any) -> dict[str, Any]:
        return {"Body": _FakeBody()}


async def _fake_storage_client() -> AsyncIterator[_FakeStorage]:
    yield _FakeStorage()


class _FakeTicketStore:
    """票据存储桩 - 固定签发、消费恒成功"""

    async def issue(self) -> str:
        return "ticket-test"

    async def consume(self, _ticket: str) -> bool:
        return True


async def _fake_ticket_store() -> AsyncIterator[_FakeTicketStore]:
    yield _FakeTicketStore()


# 覆盖外部依赖
app.dependency_overrides[get_client] = lambda: _FakeClient()
app.dependency_overrides[get_session] = lambda: _FakeSession()
app.dependency_overrides[get_storage_client] = _fake_storage_client
app.dependency_overrides[get_ticket_store] = _fake_ticket_store


@schema.parametrize()
def test_api(case):
    # WebSocket 端点仅通过 WS 协议访问 - HTTP 方法不支持检查不适用
    if case.operation.path == "/realtime/ws":
        case.call_and_validate(app=app, excluded_checks=[unsupported_method])
        return

    # Starlette 的 405 Allow 仅列出首个匹配路由的方法, 与 OpenAPI 多方法路径不一致
    if case.operation.path == "/storage/{key}":
        # 上传端点未声明请求体必需性 - 服务端对空请求体按 0 字节对象处理
        checks = [allow_header_conformance]
        if case.operation.method.upper() == "PUT":
            checks.append(negative_data_rejection)
        case.call_and_validate(app=app, excluded_checks=checks)
        return

    case.call_and_validate(app=app)
