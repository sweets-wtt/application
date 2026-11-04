"""应用配置"""

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseModel):
    """数据库配置"""

    # 连接串 - SQLite 默认本地文件, 生产切换 PostgreSQL
    # 示例: postgresql+asyncpg://app:pass@localhost:5432/app
    url: str = "sqlite+aiosqlite:///data/app.db"

    # 是否回显 SQL - 仅调试用
    echo: bool = False


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
