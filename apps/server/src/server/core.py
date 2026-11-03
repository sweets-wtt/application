"""应用核心 - 配置、常量与依赖装配"""

import os
from enum import IntEnum, StrEnum

from app.log import configure
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseModel):
    """数据库配置"""

    # 数据源名称
    url: str = "postgresql+asyncpg://app:app@localhost:5432/app"


class StorageSettings(BaseModel):
    """对象存储配置"""

    # 端点地址
    endpoint_url: str = "http://localhost:3900"

    # 访问密钥 ID
    access_key_id: str = ""

    # 私密访问密钥
    secret_access_key: str = ""

    # 区域
    region_name: str = "garage"

    # 桶名
    bucket: str = "app"


class CacheSettings(BaseModel):
    """缓存配置"""

    # 地址
    url: str = "valkey://localhost:6379/0"

    # 键前缀
    key_prefix: str = "authz:"

    # 超时秒数
    timeout: int = 60


class RealtimeSettings(BaseModel):
    """实时配置"""

    # 地址
    url: str = "valkey://localhost:6379/0"

    # 票据键前缀
    ticket_prefix: str = "rt:ticket:"

    # Pub/Sub 通道前缀
    pubsub_prefix: str = "rt:chan:"

    # 来源允许列表 - 无来源放行、带来源必须命中
    origins: list[str] = []


class WorkflowSettings(BaseModel):
    """工作流配置"""

    # 系统库连接串 - 缺省用 SQLite 落 data/, 已随 data/ 一并忽略
    system_database_url: str = "sqlite:///./data/workflow.sqlite"

    # 应用名 - 同一系统库内区分应用归属
    app_name: str = "application"


class RateLimitSettings(BaseModel):
    """限流配置"""

    # 存储地址 - 复用 Valkey 以支持多实例共享计数
    storage_uri: str = ""

    # 是否启用
    enabled: bool = True

    # 应用级默认限额 - 每客户端 IP
    default_limit: str = "300/minute"

    # 高成本端点限额 - 工作流提交
    workflow_limit: str = "30/minute"

    # 对象存储限额 - 上传下载
    storage_limit: str = "120/minute"


class Settings(BaseSettings):
    """应用配置"""

    # 模型配置
    model_config = {"env_prefix": "APP_", "env_nested_delimiter": "__"}

    # 日志级别
    log_level: str = "INFO"

    # 日志格式
    log_format: str = "console"

    # 数据库
    database: DatabaseSettings = DatabaseSettings()

    # 对象存储
    storage: StorageSettings = StorageSettings()

    # 缓存
    cache: CacheSettings = CacheSettings()

    # 实时
    realtime: RealtimeSettings = RealtimeSettings()

    # 工作流
    workflow: WorkflowSettings = WorkflowSettings()

    # 限流
    rate_limit: RateLimitSettings = RateLimitSettings()


# 应用配置实例
settings = Settings()


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


# 级别 -> 日志方法名 - warn 级写 warning 日志
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


def _instrument() -> None:
    """接线遥测 - OpenObserve 官方 SDK

    提供方与导出器由 SDK 装配, 框架埋点仍需显式启用
    """

    from openobserve import openobserve_init
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    # 追踪与指标 - 服务名取 OTEL_SERVICE_NAME
    openobserve_init(
        traces=True,
        metrics=True,
        resource_attributes={
            "service.name": os.environ.get("OTEL_SERVICE_NAME", "server")
        },
    )

    # FastAPI 埋点 - 须在应用实例化前替换类
    FastAPIInstrumentor().instrument()


def setup() -> None:
    """装配应用依赖"""

    # 日志环境变量默认值
    os.environ.setdefault("APP_LOG_LEVEL", settings.log_level)
    os.environ.setdefault("APP_LOG_FORMAT", settings.log_format)

    # 初始化日志
    configure()

    # 存在 OpenObserve 令牌才接线遥测 - 测试离线安全
    if os.environ.get("OPENOBSERVE_AUTH_TOKEN"):
        _instrument()
