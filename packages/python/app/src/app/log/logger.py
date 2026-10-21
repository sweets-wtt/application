import contextlib
import json
import logging
import os
import queue
import sys
import threading
import time
import urllib.request
from typing import Any, Final, cast

import structlog

# 敏感键
SENSITIVE_KEYS: Final[frozenset[str]] = frozenset(
    {"password", "secret", "token", "authorization", "api_key"}
)

# 默认级别
DEFAULT_LOG_LEVEL: Final[str] = "INFO"

# 上报批量上限
EXPORT_BATCH_SIZE: Final[int] = 100

# 上报间隔秒数
EXPORT_INTERVAL: Final[float] = 2.0

# 上报超时秒数
EXPORT_TIMEOUT: Final[float] = 5.0

# 级别编号
SEVERITY_NUMBERS: Final[dict[str, int]] = {
    "DEBUG": 5,
    "INFO": 9,
    "WARNING": 13,
    "ERROR": 17,
    "CRITICAL": 21,
}


def redact(
    logger: Any, method_name: str, event_dict: dict[str, Any], /
) -> dict[str, Any]:
    """脱敏敏感键"""
    for key in event_dict:
        if str(key).lower() in SENSITIVE_KEYS:
            event_dict[key] = "***"
    return event_dict


def _log_level() -> int:
    """解析日志级别"""
    name = os.environ.get("APP_LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()
    return logging.getLevelNamesMapping().get(name, logging.INFO)


def _trailing_and_renderer() -> tuple[
    list[structlog.typing.Processor], structlog.typing.Processor
]:
    """按环境返回收尾链与渲染器"""
    json_mode = os.environ.get("APP_LOG_FORMAT") == "json"
    trailing: list[structlog.typing.Processor] = [
        structlog.processors.StackInfoRenderer()
    ]
    if json_mode:
        trailing.append(structlog.processors.format_exc_info)
    trailing.append(structlog.processors.UnicodeDecoder())
    if json_mode:
        return trailing, structlog.processors.JSONRenderer()
    return trailing, structlog.dev.ConsoleRenderer()


def _sdk_disabled() -> bool:
    """是否显式禁用上报"""
    return os.environ.get("OTEL_SDK_DISABLED", "").strip().lower() in {"1", "true"}


def _otlp_headers() -> dict[str, str]:
    """解析 OTLP 导出认证头"""
    headers = {"Content-Type": "application/json"}
    raw = os.environ.get("OTEL_EXPORTER_OTLP_HEADERS", "")
    for pair in raw.split(","):
        name, _, value = pair.partition("=")
        if name.strip() and value.strip():
            headers[name.strip()] = value.strip()
    return headers


def _message(record: logging.LogRecord) -> str:
    """提取记录消息文本"""
    if isinstance(record.msg, dict):
        event = record.msg.get("event")
        return str(event) if event is not None else str(record.msg)
    return record.getMessage()


class _OtlpHandler(logging.Handler):
    """OTLP/HTTP 批量上报出口"""

    def __init__(self, endpoint: str, release: str | None = None) -> None:
        super().__init__()
        self._endpoint = endpoint.rstrip("/") + "/v1/logs"
        self._release = release
        self._queue: queue.SimpleQueue[dict[str, Any] | None] = queue.SimpleQueue()
        self._worker = threading.Thread(target=self._loop, daemon=True)
        self._worker.start()

    def emit(self, record: logging.LogRecord) -> None:
        """记录入队"""
        self._queue.put(self._payload(record))

    def close(self) -> None:
        """停机上报线程"""
        if self._worker.is_alive():
            self._queue.put(None)
        super().close()

    def _payload(self, record: logging.LogRecord) -> dict[str, Any]:
        """构造 OTLP 日志记录"""
        now = time.time_ns()
        return {
            "timeUnixNano": now,
            "observedTimeUnixNano": now,
            "severityText": record.levelname,
            "severityNumber": SEVERITY_NUMBERS.get(
                record.levelname, SEVERITY_NUMBERS["INFO"]
            ),
            "body": {"stringValue": _message(record)},
        }

    def _loop(self) -> None:
        """批量上报循环"""
        while True:
            item = self._queue.get()
            if item is None:
                return

            batch = [item]
            deadline = time.monotonic() + EXPORT_INTERVAL
            while len(batch) < EXPORT_BATCH_SIZE:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                try:
                    item = self._queue.get(timeout=remaining)
                except queue.Empty:
                    break
                if item is None:
                    self._export(batch)
                    return
                batch.append(item)

            self._export(batch)

    def _export(self, batch: list[dict[str, Any]]) -> None:
        """上报一批记录。失败静默丢弃"""
        attributes = []
        if self._release:
            attributes.append(
                {"key": "release", "value": {"stringValue": self._release}}
            )

        payload = {
            "resourceLogs": [
                {
                    "resource": {"attributes": attributes},
                    "scopeLogs": [{"logRecords": batch}],
                }
            ]
        }

        request = urllib.request.Request(
            self._endpoint,
            data=json.dumps(payload).encode(),
            headers=_otlp_headers(),
            method="POST",
        )
        with contextlib.suppress(Exception):
            urllib.request.urlopen(request, timeout=EXPORT_TIMEOUT)


def configure(endpoint: str | None = None, release: str | None = None) -> None:
    """配置日志与 OTLP 观测出口"""
    shared = cast(
        "list[structlog.typing.Processor]",
        [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            redact,
        ],
    )
    trailing, renderer = _trailing_and_renderer()

    structlog.configure(
        processors=[
            *shared,
            *trailing,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(_log_level()),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=[*shared, *trailing],
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(_log_level())
    for old in root.handlers:
        old.close()
    root.handlers = [handler]

    target = endpoint or os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if target and not _sdk_disabled():
        root.addHandler(_OtlpHandler(target, release))


def get_logger(
    name: str | None = None, **initial_values: Any
) -> structlog.stdlib.BoundLogger:
    """获取结构化日志器"""
    return structlog.get_logger(name, **initial_values)
