"""遥测服务"""

from typing import Any

from app.contracts.generated.http import TelemetryEvent
from app.log import get_logger

# 遥测日志器
log = get_logger("telemetry")


def _plain_context(context: dict[str, Any] | None) -> dict[str, str]:
    """根模型上下文转普通字典"""
    return {key: value.root for key, value in (context or {}).items()}


def record_events(service: str, release: str, events: list[TelemetryEvent]) -> int:
    """逐条写出遥测事件 返回接受条数

    error 级映射 error 日志 其余 info
    事件随 OTLP 通道进入 OpenObserve 聚合
    """
    for event in events:
        write = log.error if event.level == "error" else log.info
        write(
            "telemetry",
            service=service,
            release=release,
            fingerprint=event.fingerprint,
            context=_plain_context(event.context),
        )
    return len(events)
