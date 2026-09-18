"""遥测测试"""

import json
from typing import cast

import pytest
from app.contracts.generated.http import TelemetryEventsRequest
from app.log import configure
from fastapi import FastAPI, HTTPException, Request
from pydantic import ValidationError

from server.routes.telemetry import (
    BODY_LIMIT,
    TelemetryEventsBody,
    body_limit,
)
from server.services import telemetry as telemetry_service


def make_request() -> TelemetryEventsRequest:
    """构造合法批量请求"""
    return TelemetryEventsRequest.model_validate(
        {
            "service": "web",
            "release": "v1.2.3",
            "events": [
                {
                    "level": "error",
                    "fingerprint": "0a1b2c3d",
                    "message": "boom",
                    "timestamp": "2026-01-01T00:00:00Z",
                    "context": {"page": "home"},
                },
                {
                    "level": "warn",
                    "fingerprint": "0a1b2c3e",
                    "message": "slow",
                    "timestamp": "2026-01-01T00:00:01Z",
                },
            ],
        }
    )


def test_events_body_strict() -> None:
    """严格模型拒绝契约违约如整数时间戳"""
    with pytest.raises(ValidationError):
        TelemetryEventsBody.model_validate(
            {
                "service": "web",
                "release": "v1",
                "events": [
                    {
                        "level": "error",
                        "fingerprint": "f",
                        "message": "m",
                        "timestamp": 0,
                    }
                ],
            }
        )


async def test_body_limit() -> None:
    """请求体上限判定 超限缺失非法均按超限"""

    class FakeRequest:
        def __init__(self, headers: dict[str, str]) -> None:
            # 请求头
            self.headers = headers

    ok = await body_limit(cast("Request", FakeRequest({"content-length": "10"})))

    assert ok is None

    for headers in (
        {"content-length": str(BODY_LIMIT + 1)},
        {},
        {"content-length": "abc"},
    ):
        with pytest.raises(HTTPException) as exc:
            await body_limit(cast("Request", FakeRequest(headers)))
        assert exc.value.status_code == 413


async def test_record_events_maps_levels(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """error 级映射 error 日志 其余 info 结构化字段齐备"""
    monkeypatch.setenv("APP_LOG_FORMAT", "json")
    configure()
    accepted = telemetry_service.record_events("web", "v1.2.3", make_request().events)
    captured = capsys.readouterr().out

    assert accepted == 2
    lines = [json.loads(line) for line in captured.splitlines() if line.strip()]
    assert [line["level"] for line in lines] == ["error", "info"]
    assert lines[0]["service"] == "web"
    assert lines[0]["release"] == "v1.2.3"
    assert lines[0]["fingerprint"] == "0a1b2c3d"
    assert lines[0]["context"] == {"page": "home"}


def test_events_request_batch_limit() -> None:
    """批量超上限拒绝"""
    events = [
        {
            "level": "info",
            "fingerprint": "f",
            "message": "m",
            "timestamp": "2026-01-01T00:00:00Z",
        }
        for _ in range(101)
    ]

    with pytest.raises(ValidationError):
        TelemetryEventsRequest.model_validate(
            {"service": "web", "release": "v1", "events": events}
        )


def test_telemetry_route_registered(app: FastAPI) -> None:
    """路由已注册于应用"""
    assert app.url_path_for("create_events") == "/telemetry/events"
