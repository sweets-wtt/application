"""依赖装配测试"""

import pytest
from server.core import dependencies


def test_setup_instruments_with_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    """存在 OTLP 端点才接线遥测"""
    calls: list[bool] = []
    monkeypatch.setattr(dependencies, "configure", lambda: None)
    monkeypatch.setattr(dependencies, "_instrument", lambda: calls.append(True))
    monkeypatch.setenv("APP_LOG_LEVEL", "INFO")
    monkeypatch.setenv("APP_LOG_FORMAT", "console")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://collector:4318")

    dependencies.setup()

    assert calls == [True]


def test_setup_skips_instrumentation_without_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """缺省 OTLP 端点不接线 - 测试离线安全"""
    calls: list[bool] = []
    monkeypatch.setattr(dependencies, "configure", lambda: None)
    monkeypatch.setattr(dependencies, "_instrument", lambda: calls.append(True))
    monkeypatch.setenv("APP_LOG_LEVEL", "INFO")
    monkeypatch.setenv("APP_LOG_FORMAT", "console")
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)

    dependencies.setup()

    assert calls == []
