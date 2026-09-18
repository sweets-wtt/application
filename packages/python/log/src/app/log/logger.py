"""日志配置"""

import atexit
import contextlib
import json
import logging
import os
import queue
import sys
import threading
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any, cast

import structlog

# 敏感键
SENSITIVE_KEYS = frozenset({"password", "secret", "token", "authorization", "api_key"})

# 默认级别
DEFAULT_LOG_LEVEL = "INFO"

# OTLP 批量条数
OTLP_BATCH_SIZE = 100

# OTLP 冲刷间隔秒数
OTLP_FLUSH_INTERVAL = 5.0

# OTLP 队列上限
OTLP_QUEUE_MAX = 4096

# OTLP 级别映射
OTLP_SEVERITY = {"DEBUG": 5, "INFO": 9, "WARNING": 13, "ERROR": 17, "CRITICAL": 21}

# OTLP 传输函数类型
PostFn = Callable[[str, str], None]

# OTLP 端点 未配置则上报关闭
_otlp_endpoint: str | None = None

# OTLP 资源版本号
_otlp_release: str | None = None

# OTLP 队列
_otlp_queue: queue.Queue[str] = queue.Queue(maxsize=OTLP_QUEUE_MAX)

# OTLP 停止信号
_otlp_stop = threading.Event()

# OTLP 工作线程
_otlp_thread: threading.Thread | None = None

# OTLP 重配锁
_otlp_lock = threading.Lock()


def redact(
    logger: Any, method_name: str, event_dict: dict[str, Any], /
) -> dict[str, Any]:
    """脱敏敏感键"""
    for key in event_dict:
        if str(key).lower() in SENSITIVE_KEYS:
            event_dict[key] = "***"
    return event_dict


def _level() -> int:
    """按环境解析日志级别"""
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


def _otlp_processor(
    logger: Any, method_name: str, event_dict: dict[str, Any], /
) -> dict[str, Any]:
    """OTLP 入队处理器 入队后原样传递 下游继续渲染"""
    level = str(event_dict.get("level", "info")).upper()
    record = {
        "timeUnixNano": str(time.time_ns()),
        "severityText": level,
        "severityNumber": OTLP_SEVERITY.get(level, 9),
        "body": {
            "stringValue": json.dumps(event_dict, ensure_ascii=False, default=str)
        },
    }
    try:
        _otlp_queue.put_nowait(json.dumps(record, ensure_ascii=False))
    except queue.Full:
        # 队列满丢弃最旧 保新增
        with contextlib.suppress(queue.Empty, queue.Full):
            _otlp_queue.get_nowait()
            _otlp_queue.put_nowait(json.dumps(record, ensure_ascii=False))
    return event_dict


def _otlp_serialize(records: list[str]) -> str:
    """组装 OTLP JSON 编码请求体"""
    attributes: list[dict[str, Any]] = []
    service = os.environ.get("OTEL_SERVICE_NAME")
    if service:
        attributes.append({"key": "service.name", "value": {"stringValue": service}})
    if _otlp_release:
        attributes.append({"key": "release", "value": {"stringValue": _otlp_release}})
    payload = {
        "resourceLogs": [
            {
                "resource": {"attributes": attributes},
                "scopeLogs": [{"logRecords": [json.loads(r) for r in records]}],
            }
        ]
    }
    return json.dumps(payload, ensure_ascii=False)


def _otlp_worker() -> None:
    """OTLP 批量发送线程 停止前清空队列"""
    while True:
        batch: list[str] = []
        try:
            batch.append(_otlp_queue.get(timeout=OTLP_FLUSH_INTERVAL))
        except queue.Empty:
            if _otlp_stop.is_set():
                return
            continue
        while len(batch) < OTLP_BATCH_SIZE:
            try:
                batch.append(_otlp_queue.get_nowait())
            except queue.Empty:
                break
        # 网络失败静默丢弃 避免重试风暴
        with contextlib.suppress(OSError, urllib.error.URLError):
            _otlp_post(_otlp_endpoint or "", _otlp_serialize(batch))


def _otlp_flush() -> None:
    """同步冲刷队列全部日志"""
    batch: list[str] = []
    while True:
        try:
            batch.append(_otlp_queue.get_nowait())
        except queue.Empty:
            break
    if batch:
        # 网络失败静默丢弃 避免重试风暴
        with contextlib.suppress(OSError, urllib.error.URLError):
            _otlp_post(_otlp_endpoint or "", _otlp_serialize(batch))


def _default_post(endpoint: str, body: str) -> None:
    """默认传输 OTLP JSON 编码提交"""
    request = urllib.request.Request(
        f"{endpoint}/v1/logs",
        data=body.encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(request, timeout=5).close()


def configure(
    endpoint: str | None = None,
    release: str | None = None,
    post: PostFn | None = None,
) -> None:
    """配置日志

    structlog 与标准库日志经 ProcessorFormatter 合流输出
    endpoint 非空时启用 OTLP 上报 仅发 Collector 失败静默丢弃
    """
    global _otlp_endpoint, _otlp_release, _otlp_post, _otlp_thread

    with _otlp_lock:
        _otlp_endpoint = endpoint
        _otlp_release = release
        _otlp_post = post or _default_post
        _otlp_stop.set()
        if _otlp_thread is not None:
            _otlp_thread.join(timeout=OTLP_FLUSH_INTERVAL * 2)
            _otlp_thread = None
        _otlp_stop.clear()

    shared = cast(
        "list[structlog.typing.Processor]",
        [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            redact,
        ],
    )
    if endpoint:
        # 入队位于脱敏之后 上报内容不含敏感明文
        shared.append(_otlp_processor)
    trailing, renderer = _trailing_and_renderer()
    structlog.configure(
        processors=[
            *shared,
            *trailing,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(_level()),
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
    root.handlers = [handler]
    root.setLevel(_level())

    # 注入传输函数时由调用方控制冲刷 不启动线程
    if endpoint and post is None:
        with _otlp_lock:
            _otlp_thread = threading.Thread(
                target=_otlp_worker, daemon=True, name="otlp-logs"
            )
            _otlp_thread.start()
        atexit.register(_otlp_flush)


def get_logger(name: str | None = None, **initial_values: Any) -> Any:
    """获取结构化日志器"""
    return structlog.get_logger(name, **initial_values)
