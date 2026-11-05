"""日志配置"""

from collections.abc import MutableMapping
import logging
import os
import re
import sys
from typing import Final

import structlog


# 敏感键
SENSITIVE_KEYS: Final[frozenset[str]] = frozenset(
    {"password", "secret", "token", "authorization", "api_key"}
)

# 敏感值模式 - 覆盖键名之外的明文形态
# 顺序敏感: 先匹配更具体的形态, 再由通用键值对收尾
SENSITIVE_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    # Bearer 令牌 - 须先于通用键值对, 否则 Authorization: Bearer xxx 只脱去前缀
    re.compile(r"(?i)bearer\s+[a-z0-9._~+/-]+=*"),
    # AWS 访问密钥
    re.compile(r"AKIA[0-9A-Z]{16}"),
    # 口令键值对
    re.compile(
        r"(?i)(password|passwd|secret|token|api[_-]?key|authorization|credential)[=:]\s*\S+"
    ),
)

# 默认级别
DEFAULT_LOG_LEVEL: Final[str] = "INFO"


def _mask(value: str) -> str:
    """屏蔽字符串内嵌的敏感明文"""
    for pattern in SENSITIVE_PATTERNS:
        value = pattern.sub("***", value)
    return value


def redact(
    _logger: object, _method_name: str, event_dict: MutableMapping[str, object], /
) -> MutableMapping[str, object]:
    """脱敏敏感键与值内嵌明文"""
    for key, value in event_dict.items():
        if str(key).lower() in SENSITIVE_KEYS:
            event_dict[key] = "***"
        elif isinstance(value, str):
            event_dict[key] = _mask(value)
    return event_dict


def _level() -> int:
    """按环境解析日志级别"""
    name = os.environ.get("APP_LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()
    return logging.getLevelNamesMapping().get(name, logging.INFO)


def _trailing_and_renderer() -> tuple[list[structlog.typing.Processor], structlog.typing.Processor]:
    """按环境返回收尾链与渲染器"""
    json_mode = os.environ.get("APP_LOG_FORMAT") == "json"
    trailing: list[structlog.typing.Processor] = [structlog.processors.StackInfoRenderer()]
    if json_mode:
        trailing.append(structlog.processors.format_exc_info)
    trailing.append(structlog.processors.UnicodeDecoder())
    if json_mode:
        return trailing, structlog.processors.JSONRenderer()
    return trailing, structlog.dev.ConsoleRenderer()


def configure() -> None:
    """配置日志.

    structlog 与标准库日志经 ProcessorFormatter 合流输出
    """
    # 共享处理器
    shared: list[structlog.typing.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        redact,
    ]

    # 输出处理器
    trailing, renderer = _trailing_and_renderer()

    # structlog 配置
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

    # 标准库格式化器
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=[*shared, *trailing],
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    # 根日志器
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(_level())


def get_logger(name: str | None = None, **initial_values: object) -> structlog.stdlib.BoundLogger:
    """获取结构化日志器"""
    return structlog.get_logger(name, **initial_values)
