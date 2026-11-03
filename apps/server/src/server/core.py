"""应用核心 - 配置、常量与依赖装配"""

import os
from enum import StrEnum

from app.log import configure
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class WorkflowSettings(BaseModel):
    """工作流配置"""

    # 系统库连接串 - 缺省用 SQLite 落 data/, 已随 data/ 一并忽略
    system_database_url: str = "sqlite:///./data/workflow.sqlite"

    # 应用名 - 同一系统库内区分应用归属
    app_name: str = "application"


class RateLimitSettings(BaseModel):
    """限流配置"""

    # 是否启用
    enabled: bool = True

    # 应用级默认限额 - 每客户端 IP
    default_limit: str = "300/minute"

    # 高成本端点限额 - 工作流提交
    workflow_limit: str = "30/minute"


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

    # 工作流
    workflow: WorkflowSettings = WorkflowSettings()

    # 限流
    rate_limit: RateLimitSettings = RateLimitSettings()

    # 认证
    auth: AuthSettings = AuthSettings()


# 应用配置实例
settings = Settings()


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

# 遥测
MAX_TELEMETRY_BODY_BYTES = 256 * 1024

# 工作流
WORKFLOW_NAME = "request"


def setup() -> None:
    """装配应用依赖"""

    # 日志环境变量默认值
    os.environ.setdefault("APP_LOG_LEVEL", settings.log_level)
    os.environ.setdefault("APP_LOG_FORMAT", settings.log_format)

    # 初始化日志
    configure()
