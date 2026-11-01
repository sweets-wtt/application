"""对象存储客户端"""

from typing import TYPE_CHECKING, Self

from aiobotocore.session import AioSession
from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from contextlib import AbstractAsyncContextManager

    from aiobotocore.client import AioBaseClient


class StorageSettings(BaseSettings):
    """对象存储装配参数"""

    model_config = SettingsConfigDict(
        env_prefix="APP_STORAGE__",
        extra="ignore",
        frozen=True,
    )

    endpoint_url: str
    access_key_id: str
    secret_access_key: str
    region_name: str = "garage"
    bucket: str

    @classmethod
    def from_env(cls) -> Self:
        """从环境变量装配 - 与 compose 注入命名一致"""
        return cls()


def create_client(
    settings: StorageSettings,
) -> "AbstractAsyncContextManager[AioBaseClient]":
    """创建 S3 客户端异步上下文管理器

    返回值经 async with 进入。进入时不产生网络请求
    """
    session = AioSession()
    return session.create_client(
        "s3",
        endpoint_url=settings.endpoint_url,
        aws_access_key_id=settings.access_key_id,
        aws_secret_access_key=settings.secret_access_key,
        region_name=settings.region_name,
    )
