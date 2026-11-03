"""应用核心 - 配置、常量与依赖装配"""

import os

from app.log import configure
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class RateLimitSettings(BaseModel):
    """限流配置"""

    # 是否启用
    enabled: bool = True

    # 应用级默认限额 - 每客户端 IP
    default_limit: str = "300/minute"


class Settings(BaseSettings):
    """应用配置"""

    # 模型配置
    model_config = {"env_prefix": "APP_", "env_nested_delimiter": "__"}

    # 日志级别
    log_level: str = "INFO"

    # 日志格式
    log_format: str = "console"

    # 限流
    rate_limit: RateLimitSettings = RateLimitSettings()


# 应用配置实例
settings = Settings()


def setup() -> None:
    """装配应用依赖"""

    # 日志环境变量默认值
    os.environ.setdefault("APP_LOG_LEVEL", settings.log_level)
    os.environ.setdefault("APP_LOG_FORMAT", settings.log_format)

    # 初始化日志
    configure()
