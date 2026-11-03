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


def test_redact_masks_inline_password() -> None:
    """值内嵌口令脱敏"""
    event = redact(None, "info", {"msg": "login password=hunter2 ok"})

    assert "hunter2" not in event["msg"]
    assert "***" in event["msg"]


def test_redact_masks_bearer_token() -> None:
    """值内嵌 Bearer 令牌脱敏"""
    event = redact(None, "info", {"detail": "Authorization: Bearer abc.def-123"})

    assert "abc.def-123" not in event["detail"]


def test_redact_masks_aws_key() -> None:
    """值内嵌 AWS 访问密钥脱敏"""
    event = redact(None, "info", {"note": "key AKIAIOSFODNN7EXAMPLE used"})

    assert "AKIAIOSFODNN7EXAMPLE" not in event["note"]


def test_redact_keeps_plain_string() -> None:
    """普通字符串不受影响"""
    event = redact(None, "info", {"msg": "hello world", "count": 3})

    assert event["msg"] == "hello world"
    assert event["count"] == 3
