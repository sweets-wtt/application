"""应用配置"""

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

    # Hatchet 令牌
    token: str = ""

    # Hatchet 服务地址
    server_url: str = ""

    # TLS 策略 - 内网默认关闭
    tls_strategy: str = "none"


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


settings = Settings()
