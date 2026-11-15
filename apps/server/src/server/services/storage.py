"""对象存储服务"""

from collections.abc import AsyncIterator

from aiobotocore.client import AioBaseClient
from botocore.exceptions import ClientError

from server.adapters.storage import tenant_key
from server.core.constants import MAX_UPLOAD_SIZE
from server.core.settings import settings


class UploadTooLarge(ValueError):
    """对象上传超过上限"""


class NotFound(KeyError):
    """对象不存在"""


async def upload(
    client: AioBaseClient,
    tenant: str,
    key: str,
    stream: AsyncIterator[bytes],
) -> int:
    """流式上传对象并返回字节数。超过上限抛出 UploadTooLarge"""
    buffer = bytearray()

    # 分块累积 - 超限中止
    async for chunk in stream:
        if len(buffer) + len(chunk) > MAX_UPLOAD_SIZE:
            raise UploadTooLarge(f"上传超过 {MAX_UPLOAD_SIZE // (1024 * 1024)} MiB")
        buffer.extend(chunk)

    data = bytes(buffer)

    # 键带租户前缀写入
    await client.put_object(
        Bucket=settings.storage.bucket,
        Key=tenant_key(tenant, key),
        Body=data,
    )

    return len(data)


async def download(
    client: AioBaseClient,
    tenant: str,
    key: str,
) -> AsyncIterator[bytes]:
    """产出对象流。对象不存在抛出 NotFound"""
    try:
        result = await client.get_object(
            Bucket=settings.storage.bucket,
            Key=tenant_key(tenant, key),
        )
    except ClientError as exc:
        # 未找到键转领域异常、其余上抛
        if exc.response.get("Error", {}).get("Code") in {"NoSuchKey", "NotFound"}:
            raise NotFound(key) from exc
        raise

    body = result["Body"]

    return body.iter_chunks()
