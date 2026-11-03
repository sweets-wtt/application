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

    # 连接池常驻连接数 - 每进程
    pool_size: int = 5

    # 连接池溢出上限 - 峰值可额外申请的连接数
    max_overflow: int = 10

    # 获取连接超时秒数 - 超时抛错而非无限等待
    pool_timeout: int = 30

    # 取连接前探活 - 规避容器重启导致池内死连接
    pool_pre_ping: bool = True

    # 连接最长复用秒数 - 到点重建, 规避中间设备静默断连
    pool_recycle: int = 3600


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


class AuthSettings(BaseModel):
    """认证配置 - Casdoor OIDC"""

    # 是否启用 - 测试环境默认关闭
    enabled: bool = False

    # 签发方 - 令牌 iss 校验
    issuer: str = ""

    # 公网地址 - 浏览器跳转
    public_url: str = ""

    # 内网地址 - 服务端换取令牌与拉取 JWKS
    internal_url: str = ""

    # 客户端标识
    client_id: str = ""

    # 客户端密钥
    client_secret: str = ""

    # 回调地址
    redirect_uri: str = ""

    # 登出后回跳地址
    post_logout_redirect_uri: str = ""

    # 状态签名密钥 - 缺省回落到客户端密钥
    state_secret: str = ""

    # Cookie 是否仅 HTTPS
    cookie_secure: bool = True

    # Cookie 域 - 留空为当前主机
    cookie_domain: str = ""

    # 租户声明 - Casdoor 用户归属组织
    tenant_claim: str = "owner"

    # 角色声明
    role_claim: str = "roles"

    # JWKS 地址 - 留空按内网地址推导
    jwks_url: str = ""

    # 授权地址 - 留空按公网地址推导
    authorize_url: str = ""

    # 换令牌地址 - 留空按内网地址推导
    token_url: str = ""

    # 登出地址 - 留空按公网地址推导
    logout_url: str = ""


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

    # 认证
    auth: AuthSettings = AuthSettings()


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
    """接线遥测 - 标准 OTel SDK 经 Collector 导出

    追踪与指标统一走 OTLP, 后端由 Collector 决定
    """

    from opentelemetry import metrics, trace
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
        OTLPMetricExporter,
    )
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    # 资源 - 服务名取 OTEL_SERVICE_NAME
    resource = Resource.create(
        {"service.name": os.environ.get("OTEL_SERVICE_NAME", "server")}
    )

    # 追踪提供方 - OTLP 批处理导出
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(tracer_provider)

    # 指标提供方 - OTLP 周期导出
    metrics.set_meter_provider(
        MeterProvider(
            resource=resource,
            metric_readers=[
                PeriodicExportingMetricReader(
                    OTLPMetricExporter(),
                    export_interval_millis=int(
                        os.environ.get("OTEL_METRIC_EXPORT_INTERVAL", "60000")
                    ),
                )
            ],
        )
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

    # 存在 OTLP 端点才接线遥测 - 测试离线安全
    if any(
        os.environ.get(key)
        for key in (
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT",
        )
    ):
        _instrument()
