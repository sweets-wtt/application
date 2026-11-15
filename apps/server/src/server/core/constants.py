"""应用常量 - 集中魔法数字与默认值"""

from enum import IntEnum, StrEnum


class WsCloseCode(IntEnum):
    """WebSocket 关闭码 - 私有区间 4000-4999"""

    ORIGIN_DENIED = 4403
    TICKET_STORE_UNAVAILABLE = 4503
    TICKET_INVALID = 4401


class MessageType(StrEnum):
    """实时消息类型 - 协议信封 type 字段"""

    PING = "ping"
    PONG = "pong"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    PUBLISH = "publish"
    EVENT = "event"
    SYSTEM = "system"


class TelemetryLevel(StrEnum):
    """遥测事件级别"""

    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


# 级别 → 日志方法名 - warn 级写 warning 日志
LEVEL_LOG_METHODS: dict[TelemetryLevel, str] = {
    TelemetryLevel.DEBUG: "debug",
    TelemetryLevel.INFO: "info",
    TelemetryLevel.WARN: "warning",
    TelemetryLevel.ERROR: "error",
}

# 实时票据
TICKET_TOKEN_BYTES = 32
TICKET_TTL_SECONDS = 30
TICKET_ISSUE_ATTEMPTS = 3

# 出站队列上限 - 对齐 @app/realtime 默认值
REALTIME_QUEUE_LIMIT = 100

# 对象存储
MAX_UPLOAD_SIZE = 10 * 1024 * 1024

# 遥测
MAX_TELEMETRY_BODY_BYTES = 256 * 1024

# 工作流
WORKFLOW_NAME = "request"
