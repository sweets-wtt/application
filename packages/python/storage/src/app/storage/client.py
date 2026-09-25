"""对象存储客户端"""

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from aiobotocore.session import AioSession

if TYPE_CHECKING:
    from contextlib import AbstractAsyncContextManager

    from aiobotocore.client import AioBaseClient


@dataclass(frozen=True)
class StorageSettings:
    """对象存储装配参数"""

    endpoint_url: str
    access_key_id: str
    secret_access_key: str
    region_name: str
    bucket: str

    @classmethod
    def from_env(cls) -> Self:
        """从环境变量装配"""
        return cls(
            endpoint_url=os.environ["APP_STORAGE_ENDPOINT"],
            access_key_id=os.environ["APP_STORAGE_ACCESS_KEY"],
            secret_access_key=os.environ["APP_STORAGE_SECRET_KEY"],
            region_name=os.environ.get("APP_STORAGE_REGION", "garage"),
            bucket=os.environ["APP_STORAGE_BUCKET"],
        )


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
