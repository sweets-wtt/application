"""日志测试"""

import json

import pytest
from app.log import configure, get_logger
from app.log import logger as logger_module
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


def test_otlp_disabled_without_endpoint() -> None:
    """未配置端点时不启用 OTLP 上报"""
    configure()

    assert logger_module._otlp_endpoint is None
    assert logger_module._otlp_thread is None


def test_otlp_flush_posts_resource_logs() -> None:
    """冲刷提交 OTLP JSON 编码 脱敏与版本号生效"""
    posts: list[tuple[str, str]] = []

    def post(endpoint: str, body: str) -> None:
        posts.append((endpoint, body))

    configure(endpoint="http://collector:4318", release="v1.2.3", post=post)
    log = get_logger("test")
    log.info("hello", user="app", token="abc")
    logger_module._otlp_flush()

    endpoint, body = posts[0]
    assert endpoint == "http://collector:4318"
    payload = json.loads(body)
    resource_logs = payload["resourceLogs"][0]
    attributes = {
        item["key"]: item["value"]["stringValue"]
        for item in resource_logs["resource"]["attributes"]
    }
    assert attributes["release"] == "v1.2.3"
    record = resource_logs["scopeLogs"][0]["logRecords"][0]
    assert record["severityText"] == "INFO"
    assert record["severityNumber"] == 9
    body_data = json.loads(record["body"]["stringValue"])
    assert body_data["event"] == "hello"
    assert body_data["token"] == "***"


def test_otlp_post_failure_dropped() -> None:
    """提交失败静默丢弃 不重试"""

    def post(endpoint: str, body: str) -> None:
        raise OSError("网络不可用")

    configure(endpoint="http://collector:4318", post=post)
    get_logger("test").info("hello")
    logger_module._otlp_flush()


def test_otlp_queue_full_drops_oldest() -> None:
    """队列满丢弃最旧"""
    posts: list[tuple[str, str]] = []

    def post(endpoint: str, body: str) -> None:
        posts.append((endpoint, body))

    configure(endpoint="http://collector:4318", post=post)
    for index in range(logger_module.OTLP_QUEUE_MAX + 1):
        logger_module._otlp_processor(
            None, "info", {"event": str(index), "level": "info"}
        )
    logger_module._otlp_flush()

    payload = json.loads(posts[0][1])
    records = payload["resourceLogs"][0]["scopeLogs"][0]["logRecords"]
    assert len(records) == logger_module.OTLP_QUEUE_MAX
