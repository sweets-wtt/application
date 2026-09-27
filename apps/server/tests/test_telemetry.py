"""遥测接收测试"""

from collections.abc import Iterator

import pytest
from app.contracts.generated.http import TelemetryEvent, TelemetryIngest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from server.services import telemetry as telemetry_service


class StubLogger:
    """日志调用记录桩"""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict[str, object]]] = []

    def debug(self, event: str, **kwargs: object) -> None:
        """记录 debug 调用"""
        self.calls.append(("debug", event, kwargs))

    def info(self, event: str, **kwargs: object) -> None:
        """记录 info 调用"""
        self.calls.append(("info", event, kwargs))

    def warning(self, event: str, **kwargs: object) -> None:
        """记录 warning 调用"""
        self.calls.append(("warning", event, kwargs))

    def error(self, event: str, **kwargs: object) -> None:
        """记录 error 调用"""
        self.calls.append(("error", event, kwargs))


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    """遥测测试客户端"""
    with TestClient(app) as test_client:
        yield test_client


def event(**overrides: object) -> dict[str, object]:
    """构造合法事件"""
    base: dict[str, object] = {
        "level": "error",
        "fingerprint": "TypeError:boom",
        "message": "boom",
        "timestamp": 1_700_000_000_000,
    }
    base.update(overrides)
    return base


def payload(**overrides: object) -> dict[str, object]:
    """构造合法载荷"""
    base: dict[str, object] = {
        "service": "web",
        "release": "1.2.3",
        "events": [event()],
    }
    base.update(overrides)
    return base


def test_http_accepts_events(client: TestClient) -> None:
    """批量事件受理 - 202"""
    response = client.post(
        "/telemetry/events", json=payload(events=[event(), event(level="info")])
    )

    assert response.status_code == 202

    body = response.json()
    assert body["code"] == 0
    assert body["message"] == "ok"
    assert body["data"] == {"accepted": 2}


def test_http_rejects_unknown_field(client: TestClient) -> None:
    """事件附加未知字段被拒 - 严格 schema"""
    response = client.post(
        "/telemetry/events", json=payload(events=[event(unknown="x")])
    )

    assert response.status_code == 422


def test_http_rejects_invalid_service(client: TestClient) -> None:
    """服务枚举校验"""
    response = client.post("/telemetry/events", json=payload(service="desktop"))

    assert response.status_code == 422


def test_http_rejects_oversize_batch(client: TestClient) -> None:
    """批量条数超上限被拒 - 101 条"""
    response = client.post(
        "/telemetry/events", json=payload(events=[event() for _ in range(101)])
    )

    assert response.status_code == 422


def test_http_rejects_oversize_body(client: TestClient) -> None:
    """请求体超上限被拒 - 413"""
    events = [event(message="x" * 4000) for _ in range(100)]
    response = client.post("/telemetry/events", json=payload(events=events))

    assert response.status_code == 413
    assert "256 KiB" in response.json()["detail"]


async def test_level_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    """级别映射 - error 级写 error 日志"""
    stub = StubLogger()
    monkeypatch.setattr(telemetry_service, "logger", stub)
    ingest = TelemetryIngest(
        service="miniapp",
        release="2.0.0",
        events=[
            TelemetryEvent(level=level, fingerprint="f", message="m", timestamp=1)
            for level in ("debug", "info", "warn", "error")
        ],
    )

    accepted = await telemetry_service.ingest(ingest)

    assert accepted == 4
    assert [name for name, _, _ in stub.calls] == [
        "debug",
        "info",
        "warning",
        "error",
    ]

    _, name, kwargs = stub.calls[-1]
    assert name == "telemetry.event"
    assert kwargs["service"] == "miniapp"
    assert kwargs["release"] == "2.0.0"
    assert kwargs["level"] == "error"
    assert kwargs["fingerprint"] == "f"
