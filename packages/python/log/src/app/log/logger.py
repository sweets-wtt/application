"""日志配置"""

import logging
import os
import sys
from typing import Any, cast

import structlog

# 敏感键
SENSITIVE_KEYS = frozenset({"password", "secret", "token", "authorization", "api_key"})

# 默认级别
DEFAULT_LOG_LEVEL = "INFO"


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


def configure() -> None:
    """配置日志

    structlog 与标准库日志经 ProcessorFormatter 合流输出
    """
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


def get_logger(name: str | None = None, **initial_values: Any) -> Any:
    """获取结构化日志器"""
    return structlog.get_logger(name, **initial_values)
