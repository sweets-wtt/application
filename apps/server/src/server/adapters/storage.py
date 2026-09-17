"""对象存储适配器 - https://aiobotocore.aio-libs.org/en/latest/examples/s3/basic_usage.html

客户端为异步上下文管理器 进入后可用 退出自动关闭
api 每请求经 get_storage worker Task 经 open_client 复用同一薄接口
"""

from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from typing import Final

from aiobotocore.client import AioBaseClient
from aiobotocore.response import AioStreamingBody
from app.storage import create_client

from server.core.settings import storage_settings

# 流式上传上限 10 MiB
MAX_OBJECT_SIZE: Final[int] = 10 * 1024 * 1024

# 流式分块大小 1 MiB
CHUNK_SIZE: Final[int] = 1024 * 1024

# 默认租户
DEFAULT_TENANT: Final[str] = "default"


class PayloadTooLargeError(Exception):
    """对象超过流式上传上限"""


def object_key(tenant: str, path: str) -> str:
    """租户前缀对象键 {tenant}/{path}"""
    return f"{tenant}/{path}"


@asynccontextmanager
async def open_client() -> AsyncGenerator[AioBaseClient, None]:
    """打开 S3 客户端 退出自动关闭"""
    async with create_client(
        endpoint_url=storage_settings.storage.url,
        region_name=storage_settings.storage.region,
        aws_access_key_id=storage_settings.storage.access_key_id,
        aws_secret_access_key=storage_settings.storage.secret_access_key,
    ) as client:
        yield client


async def get_storage() -> AsyncGenerator[AioBaseClient, None]:
    """每请求 S3 客户端 退出自动关闭"""
    async with open_client() as client:
        yield client


async def upload(
    client: AioBaseClient,
    bucket: str,
    key: str,
    stream: AsyncIterator[bytes],
) -> int:
    """分块流式上传 返回对象字节数

    Raises: 累计超过 MAX_OBJECT_SIZE 抛 PayloadTooLargeError
    """
    buffers: list[bytes] = []
    size = 0
    async for chunk in stream:
        size += len(chunk)
        if size > MAX_OBJECT_SIZE:
            raise PayloadTooLargeError(f"对象超过流式上传上限 {MAX_OBJECT_SIZE} 字节")
        buffers.append(chunk)
    await client.put_object(Bucket=bucket, Key=key, Body=b"".join(buffers))
    return size


async def open_object(
    client: AioBaseClient,
    bucket: str,
    key: str,
) -> AioStreamingBody:
    """打开对象体 get_object 即时调用 供流式读取"""
    response = await client.get_object(Bucket=bucket, Key=key)
    return response["Body"]


async def iter_chunks(body: AioStreamingBody) -> AsyncIterator[bytes]:
    """按块迭代对象体"""
    async for chunk in body.iter_chunks(CHUNK_SIZE):
        yield chunk
