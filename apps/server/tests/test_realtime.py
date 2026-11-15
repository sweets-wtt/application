"""实时测试"""

import json
import string
import time
from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from server.adapters.realtime import TicketStore, get_ticket_store
from server.core.constants import (
    REALTIME_QUEUE_LIMIT,
    TICKET_TTL_SECONDS,
    WsCloseCode,
)
from server.core.settings import settings
from server.services import realtime as realtime_service
from starlette.websockets import WebSocketDisconnect
from valkey.exceptions import ValkeyError


class FakeValkey:
    """内存票据存储"""

    def __init__(self) -> None:
        self.data: dict[str, str] = {}
        self.set_calls: list[tuple[str, str, bool, int]] = []
        self.failed = False

    async def set(self, name: str, value: str, *, nx: bool, ex: int) -> object:
        """写入并记录调用 - NX 冲突返回 None"""
        if self.failed:
            raise ValkeyError("票据存储不可用")
        self.set_calls.append((name, value, nx, ex))
        if nx and name in self.data:
            return None
        self.data[name] = value
        return True

    async def getdel(self, name: str) -> object | None:
        """取出即删除"""
        if self.failed:
            raise ValkeyError("票据存储不可用")
        return self.data.pop(name, None)

    async def aclose(self) -> None:
        """无操作"""
        pass


@pytest.fixture
def fake() -> FakeValkey:
    """内存 Valkey 后端"""
    return FakeValkey()


@pytest.fixture
def store(fake: FakeValkey) -> TicketStore:
    """票据存储"""
    return TicketStore(fake, "rt:ticket:")


@pytest.fixture
def client(app: FastAPI, store: TicketStore) -> Iterator[TestClient]:
    """注入内存票据存储的客户端"""
    app.dependency_overrides[get_ticket_store] = lambda: store
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_ticket_store, None)


def issue(client: TestClient) -> str:
    """签发票据"""
    response = client.post("/realtime/ticket")
    assert response.status_code == 200
    return response.json()["data"]["ticket"]


async def test_issue_256bit_ticket(store: TicketStore, fake: FakeValkey) -> None:
    """签发 256 bit 票据 - SET NX EX 30"""
    ticket = await store.issue()
    assert len(ticket) == 43
    assert set(ticket) <= set(string.ascii_letters + string.digits + "-_")

    name, value, nx, ex = fake.set_calls[0]
    assert name == f"rt:ticket:{ticket}"
    assert value == "1"
    assert nx is True
    assert ex == TICKET_TTL_SECONDS == 30


async def test_consume_one_time(store: TicketStore) -> None:
    """票据一次性 - GETDEL"""
    ticket = await store.issue()

    assert await store.consume(ticket) is True
    assert await store.consume(ticket) is False


async def test_consume_unknown(store: TicketStore) -> None:
    """未签发票据无效"""
    assert await store.consume("unknown") is False


def test_issue_ticket_contract(client: TestClient) -> None:
    """票据端点响应契约与过期时间"""
    before = int(time.time() * 1000)
    response = client.post("/realtime/ticket")
    assert response.status_code == 200

    body = response.json()
    assert body["code"] == 0
    assert body["message"] == "ok"
    assert len(body["data"]["ticket"]) == 43
    assert body["data"]["expiresAtMs"] >= before + 30_000


def test_issue_allows_missing_origin(client: TestClient) -> None:
    """无来源放行 - 非浏览器客户端"""
    assert client.post("/realtime/ticket").status_code == 200


def test_issue_rejects_foreign_origin(client: TestClient) -> None:
    """来源不在允许列表被拒 - 默认空列表 fail-closed"""
    response = client.post(
        "/realtime/ticket", headers={"origin": "https://evil.example"}
    )
    assert response.status_code == 403


def test_issue_allows_listed_origin(
    monkeypatch: pytest.MonkeyPatch, client: TestClient
) -> None:
    """来源命中允许列表放行"""
    monkeypatch.setattr(settings.realtime, "origins", ["https://app.example"])
    response = client.post(
        "/realtime/ticket", headers={"origin": "https://app.example"}
    )
    assert response.status_code == 200


def test_issue_unavailable(client: TestClient, fake: FakeValkey) -> None:
    """票据存储不可用返回 503"""
    fake.failed = True
    assert client.post("/realtime/ticket").status_code == 503


def test_ws_connect_and_pong(client: TestClient) -> None:
    """连接就绪事件与心跳"""
    ticket = issue(client)
    with client.websocket_connect(f"/realtime/ws?ticket={ticket}") as websocket:
        hello = json.loads(websocket.receive_text())
        assert hello == {
            "type": "event",
            "topic": "system",
            "payload": {"status": "connected"},
        }
        assert realtime_service.hub.size == 1

        websocket.send_text("ping")
        assert websocket.receive_text() == "pong"

    assert realtime_service.hub.size == 0


def test_ws_ticket_one_time(client: TestClient) -> None:
    """票据一次性 - 重连被拒"""
    ticket = issue(client)
    with client.websocket_connect(f"/realtime/ws?ticket={ticket}") as websocket:
        websocket.receive_text()
    with (
        pytest.raises(WebSocketDisconnect),
        client.websocket_connect(f"/realtime/ws?ticket={ticket}") as websocket,
    ):
        websocket.receive_text()


def test_ws_rejects_unknown_ticket(client: TestClient) -> None:
    """未签发票据被拒"""
    with (
        pytest.raises(WebSocketDisconnect),
        client.websocket_connect("/realtime/ws?ticket=unknown") as websocket,
    ):
        websocket.receive_text()


def test_ws_rejects_foreign_origin(client: TestClient) -> None:
    """来源不在允许列表拒绝连接"""
    with (
        pytest.raises(WebSocketDisconnect),
        client.websocket_connect(
            "/realtime/ws?ticket=whatever",
            headers={"origin": "https://evil.example"},
        ) as websocket,
    ):
        websocket.receive_text()


def test_ws_allows_listed_origin(
    monkeypatch: pytest.MonkeyPatch, client: TestClient
) -> None:
    """来源命中允许列表连接成功"""
    monkeypatch.setattr(settings.realtime, "origins", ["https://app.example"])
    ticket = issue(client)
    with client.websocket_connect(
        f"/realtime/ws?ticket={ticket}",
        headers={"origin": "https://app.example"},
    ) as websocket:
        assert json.loads(websocket.receive_text())["type"] == "event"


def test_ws_unavailable(client: TestClient, fake: FakeValkey) -> None:
    """票据存储不可用拒绝连接 - 关闭码 4503"""
    fake.failed = True

    with (
        pytest.raises(WebSocketDisconnect) as excinfo,
        client.websocket_connect("/realtime/ws?ticket=whatever") as websocket,
    ):
        websocket.receive_text()

    assert excinfo.value.code == WsCloseCode.TICKET_STORE_UNAVAILABLE


async def test_queue_drops_oldest() -> None:
    """出站有界队列满丢最旧"""
    sent: list[str] = []

    async def send(data: str) -> None:
        sent.append(data)

    connection = realtime_service.Connection(send)
    for index in range(REALTIME_QUEUE_LIMIT + 1):
        connection.enqueue(f"e{index}")

    assert connection.pending == REALTIME_QUEUE_LIMIT

    await connection.flush()
    assert sent[0] == "e1"
    assert len(sent) == REALTIME_QUEUE_LIMIT


async def test_build_event_contract_shape() -> None:
    """事件信封结构"""
    payload = realtime_service.build_event("topic", {"k": "v"})
    assert json.loads(payload) == {
        "type": "event",
        "topic": "topic",
        "payload": {"k": "v"},
    }


async def test_hub_broadcast_and_disconnect() -> None:
    """广播与摘除"""
    sent: list[str] = []

    async def send(data: str) -> None:
        sent.append(data)

    hub = realtime_service.Hub()
    connection = realtime_service.Connection(send)
    hub.connect(connection)

    await hub.broadcast("one")
    assert sent == ["one"]

    hub.disconnect(connection)
    await hub.broadcast("two")
    assert sent == ["one"]


async def test_hub_drops_failed_connection() -> None:
    """广播失败摘除连接"""

    async def send(data: str) -> None:
        raise RuntimeError("连接已断")

    hub = realtime_service.Hub()
    connection = realtime_service.Connection(send)
    hub.connect(connection)

    await hub.broadcast("one")
    await hub.broadcast("two")
    assert hub.size == 0
