"""对象存储适配器"""

from collections.abc import AsyncIterator

from aiobotocore.client import AioBaseClient
from app.storage import StorageSettings, create_client

from server.core.settings import settings

# 客户端装配参数
client_settings = StorageSettings(
    endpoint_url=settings.storage.endpoint_url,
    access_key_id=settings.storage.access_key_id,
    secret_access_key=settings.storage.secret_access_key,
    region_name=settings.storage.region_name,
    bucket=settings.storage.bucket,
)


def tenant_key(tenant: str, key: str) -> str:
    """租户前缀对象键"""
    return f"{tenant}/{key}"


async def get_client() -> AsyncIterator[AioBaseClient]:
    """每请求生命周期的存储客户端"""
    async with create_client(client_settings) as client:
        yield client
