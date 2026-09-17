"""对象存储服务"""

from collections.abc import AsyncIterator

from aiobotocore.client import AioBaseClient
from aiobotocore.response import AioStreamingBody

from server.adapters import storage
from server.core.settings import storage_settings


async def upload_object(
    client: AioBaseClient,
    tenant: str,
    path: str,
    stream: AsyncIterator[bytes],
) -> str:
    """上传对象到租户前缀 返回对象键"""
    key = storage.object_key(tenant, path)
    await storage.upload(client, storage_settings.storage.bucket, key, stream)
    return key


async def open_object(
    client: AioBaseClient,
    tenant: str,
    path: str,
) -> AioStreamingBody:
    """打开租户前缀对象体 供流式读取"""
    key = storage.object_key(tenant, path)
    return await storage.open_object(client, storage_settings.storage.bucket, key)
