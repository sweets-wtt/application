"""对象存储适配器测试"""

from collections.abc import AsyncIterator
from typing import Any, cast

import pytest
from aiobotocore.client import AioBaseClient
from server.adapters import storage
from server.services import storage as storage_service


class StubBody:
    """流式对象体桩"""

    def __init__(self, data: bytes) -> None:
        # 对象内容
        self.data = data

    async def iter_chunks(self, chunk_size: int) -> AsyncIterator[bytes]:
        """按块迭代"""
        for start in range(0, len(self.data), chunk_size):
            yield self.data[start : start + chunk_size]


class StubClient:
    """S3 客户端桩 记录 put 返回 get"""

    def __init__(self) -> None:
        # 对象表
        self.objects: dict[str, bytes] = {}

    async def put_object(self, Bucket: str, Key: str, Body: bytes, **_: Any) -> None:
        """记录上传"""
        self.objects[Key] = Body

    async def get_object(self, Bucket: str, Key: str, **_: Any) -> dict[str, Any]:
        """返回对象体"""
        return {"Body": StubBody(self.objects[Key])}


def make_client() -> AioBaseClient:
    """桩客户端替代真实客户端 类型对齐适配器入参"""
    return cast("AioBaseClient", StubClient())


async def stream_bytes(data: bytes, size: int) -> AsyncIterator[bytes]:
    """按指定块大小切分数据"""
    for start in range(0, len(data), size):
        yield data[start : start + size]


async def test_open_client() -> None:
    """客户端可打开 退出自动关闭"""
    async with storage.open_client() as client:
        assert isinstance(client, AioBaseClient)


async def test_object_key() -> None:
    """租户前缀对象键"""
    assert storage.object_key("acme", "a/b.txt") == "acme/a/b.txt"
    assert storage.object_key(storage.DEFAULT_TENANT, "a.txt") == "default/a.txt"


async def test_upload_stream() -> None:
    """分块流式上传记录对象 返回字节数"""
    client = make_client()
    size = await storage.upload(client, "bucket", "k", stream_bytes(b"hello", 2))

    assert size == 5
    assert client.objects["k"] == b"hello"


async def test_upload_too_large() -> None:
    """超过 10 MiB 上限拒绝且不落对象"""
    client = make_client()
    data = b"x" * (storage.MAX_OBJECT_SIZE + 1)

    with pytest.raises(storage.PayloadTooLargeError, match="对象超过流式上传上限"):
        await storage.upload(
            client, "bucket", "k", stream_bytes(data, storage.CHUNK_SIZE)
        )

    assert client.objects == {}


async def test_download_stream() -> None:
    """打开对象体并按块还原"""
    client = make_client()
    await storage.upload(client, "bucket", "k", stream_bytes(b"hello", 2))
    body = await storage.open_object(client, "bucket", "k")
    received = b"".join([chunk async for chunk in storage.iter_chunks(body)])

    assert received == b"hello"


async def test_service_upload_object() -> None:
    """服务层组装租户前缀与桶名"""
    client = make_client()
    key = await storage_service.upload_object(
        client, "acme", "a.txt", stream_bytes(b"data", 4)
    )

    assert key == "acme/a.txt"
    assert client.objects["acme/a.txt"] == b"data"


async def test_service_open_object() -> None:
    """服务层按租户前缀打开对象体"""
    client = make_client()
    await storage_service.upload_object(
        client, "acme", "a.txt", stream_bytes(b"data", 4)
    )
    body = await storage_service.open_object(client, "acme", "a.txt")
    received = b"".join([chunk async for chunk in storage.iter_chunks(body)])

    assert received == b"data"
