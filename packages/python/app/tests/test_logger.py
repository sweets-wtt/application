import logging

import pytest
from app.log import configure, get_logger
from app.log.logger import _OtlpHandler, redact


def test_configure_and_get_logger(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """配置后可获取日志器并渲染输出"""
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)

    configure()
    log = get_logger("test")
    log.info("hello", user="app")

    captured = capsys.readouterr()

    assert "hello" in captured.out


def test_redact_masks_sensitive_keys() -> None:
    """敏感键脱敏"""
    event = redact(None, "info", {"token": "abc", "user": "app"})

    assert event["token"] == "***"
    assert event["user"] == "app"


def test_configure_otlp_default_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """默认开启上报并注册出口"""
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://127.0.0.1:9")
    monkeypatch.delenv("OTEL_SDK_DISABLED", raising=False)

    configure(release="vtest")

    exporters = [
        handler
        for handler in logging.getLogger().handlers
        if isinstance(handler, _OtlpHandler)
    ]

    assert len(exporters) == 1
    for handler in exporters:
        handler.close()


def test_configure_otlp_sdk_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """显式禁用后不注册出口"""
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://127.0.0.1:9")
    monkeypatch.setenv("OTEL_SDK_DISABLED", "true")

    configure()

    exporters = [
        handler
        for handler in logging.getLogger().handlers
        if isinstance(handler, _OtlpHandler)
    ]

    assert not exporters
