"""应用配置"""

from pydantic import BaseModel
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


class DatabaseConfig(BaseModel):
    """数据库连接配置"""

    # 连接 URL
    url: str


class DatabaseSettings(BaseSettings):
    """数据库环境配置"""

    # 模型配置 官方双下划线嵌套分隔符 DATABASE__URL -> database.url
    model_config = {"env_nested_delimiter": "__"}

    # 数据库
    database: DatabaseConfig


db_settings = DatabaseSettings()


class StorageConfig(BaseModel):
    """对象存储连接配置"""

    # 端点 URL
    url: str

    # 区域
    region: str

    # 访问密钥
    access_key_id: str

    # 秘密密钥
    secret_access_key: str

    # 桶名
    bucket: str


class StorageSettings(BaseSettings):
    """对象存储环境配置"""

    # 模型配置 官方双下划线嵌套分隔符 STORAGE__URL -> storage.url
    model_config = {"env_nested_delimiter": "__"}

    # 对象存储
    storage: StorageConfig


storage_settings = StorageSettings()
