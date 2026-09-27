"""遥测接收服务"""

from app.contracts.generated.http import TelemetryIngest
from app.log import get_logger

from server.core.constants import LEVEL_LOG_METHODS, TelemetryLevel

# 结构化日志器
logger = get_logger(__name__)


async def ingest(payload: TelemetryIngest) -> int:
    """逐条结构化写出遥测事件 - 返回受理条数"""
    for event in payload.events:
        level = TelemetryLevel(event.level)
        method = getattr(logger, LEVEL_LOG_METHODS[level])
        method(
            "telemetry.event",
            service=payload.service,
            release=payload.release,
            level=event.level,
            fingerprint=event.fingerprint,
            message=event.message,
            timestamp=event.timestamp,
            context=event.context,
        )

    return len(payload.events)
