"""日志测试"""

import pytest
from app.log import configure, get_logger
from app.log.logger import redact


def test_configure_and_get_logger(capsys: pytest.CaptureFixture[str]) -> None:
    """配置后可获取日志器并渲染输出"""
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
