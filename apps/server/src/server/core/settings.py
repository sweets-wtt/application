"""应用配置"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 模型配置
    model_config = {"env_prefix": "APP_"}

    # 日志级别
    log_level: str = "INFO"

    # 日志格式
    log_format: str = "console"


settings = Settings()
