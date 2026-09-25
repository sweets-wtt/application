"""应用配置"""

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseModel):
    """数据库配置"""

    # 数据源名称
    url: str = "postgresql+asyncpg://app:app@localhost:5432/app"


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


settings = Settings()
