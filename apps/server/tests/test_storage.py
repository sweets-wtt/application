"""对象存储测试"""

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, cast

import httpx2
import pytest
from botocore.exceptions import ClientError
from fastapi import FastAPI
from server.adapters.storage import get_client, tenant_key
from server.core.constants import MAX_UPLOAD_SIZE
from server.main import app as application
from server.services import storage as storage_service

if TYPE_CHECKING:
    from aiobotocore.client import AioBaseClient


class FakeBody:
    """响应体流"""

    def __init__(self, data: bytes) -> None:
        self._data = data

    async def iter_chunks(self, chunk_size: int = 1024) -> AsyncIterator[bytes]:
        """分块产出"""
        for start in range(0, len(self._data), chunk_size):
            yield self._data[start : start + chunk_size]


class FakeClient:
    """内存对象存储客户端桩"""

    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    async def put_object(
        self,
        *,
        Bucket: str,
        Key: str,
        Body: bytes,
        **kwargs: object,
    ) -> dict[str, object]:
        """写入内存"""
        self.objects[Key] = Body
        return {}

    async def get_object(
        self,
        *,
        Bucket: str,
        Key: str,
        **kwargs: object,
    ) -> dict[str, object]:
        """读取内存"""
        if Key not in self.objects:
            raise ClientError(
                {"Error": {"Code": "NoSuchKey", "Message": Key}},
                "GetObject",
            )
        return {"Body": FakeBody(self.objects[Key])}


async def stream_of(*chunks: bytes) -> AsyncIterator[bytes]:
    """产出固定分块"""
    for chunk in chunks:
        yield chunk


@pytest.fixture
def stub_client() -> Iterator[FakeClient]:
    """内存客户端替换依赖"""
    fake = FakeClient()
    application.dependency_overrides[get_client] = lambda: fake
    yield fake
    application.dependency_overrides.pop(get_client, None)


@pytest.fixture
async def client(
    app: FastAPI, stub_client: FakeClient
) -> AsyncIterator[httpx2.AsyncClient]:
    """ASGI 测试客户端"""
    transport = httpx2.ASGITransport(app=app)
    async with httpx2.AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        yield client


def test_tenant_key_prefixes_tenant() -> None:
    """对象键带租户前缀"""
    assert tenant_key("acme", "docs/readme.md") == "acme/docs/readme.md"


async def test_upload_streams_with_prefix() -> None:
    """流式上传写入租户前缀键"""
    fake = FakeClient()
    client = cast("AioBaseClient", fake)

    size = await storage_service.upload(
        client, "acme", "a.txt", stream_of(b"hello", b" world")
    )

    assert size == 11
    assert fake.objects == {"acme/a.txt": b"hello world"}


async def test_upload_rejects_oversize() -> None:
    """超过上限中止且不写入"""
    fake = FakeClient()
    client = cast("AioBaseClient", fake)
    stream = stream_of(b"x" * MAX_UPLOAD_SIZE, b"y")

    with pytest.raises(storage_service.UploadTooLarge):
        await storage_service.upload(client, "acme", "big.bin", stream)

    assert fake.objects == {}


async def test_download_yields_object() -> None:
    """流式下载产出对象内容"""
    fake = FakeClient()
    fake.objects["acme/a.txt"] = b"hello world"
    client = cast("AioBaseClient", fake)

    stream = await storage_service.download(client, "acme", "a.txt")
    chunks = [chunk async for chunk in stream]

    assert b"".join(chunks) == b"hello world"


async def test_download_missing_object() -> None:
    """对象不存在抛出 NotFound"""
    fake = FakeClient()
    client = cast("AioBaseClient", fake)

    with pytest.raises(storage_service.NotFound):
        await storage_service.download(client, "acme", "missing.txt")


async def test_http_put_streams_object(
    client: httpx2.AsyncClient, stub_client: FakeClient
) -> None:
    """经 HTTP 流式上传对象"""
    response = await client.put(
        "/storage/a.txt",
        headers={"x-tenant": "acme"},
        content=stream_of(b"hello", b" world"),
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "message": "ok",
        "data": {"key": "a.txt", "size": 11},
    }
    assert stub_client.objects == {"acme/a.txt": b"hello world"}


async def test_http_put_rejects_oversize(
    client: httpx2.AsyncClient, stub_client: FakeClient
) -> None:
    """经 HTTP 上传超过上限被拒"""
    response = await client.put(
        "/storage/big.bin",
        headers={"x-tenant": "acme"},
        content=stream_of(b"x" * MAX_UPLOAD_SIZE, b"y"),
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "上传超过 10 MiB"
    assert stub_client.objects == {}


async def test_http_put_requires_tenant_header(
    client: httpx2.AsyncClient, stub_client: FakeClient
) -> None:
    """缺租户头被拒"""
    response = await client.put("/storage/a.txt", content=b"hello")

    assert response.status_code == 422
    assert stub_client.objects == {}


async def test_http_get_object(
    client: httpx2.AsyncClient, stub_client: FakeClient
) -> None:
    """经 HTTP 下载对象"""
    stub_client.objects["acme/a.txt"] = b"hello world"
    response = await client.get("/storage/a.txt", headers={"x-tenant": "acme"})

    assert response.status_code == 200
    assert response.content == b"hello world"
    assert response.headers["content-type"] == "application/octet-stream"


async def test_http_get_missing_object(client: httpx2.AsyncClient) -> None:
    """经 HTTP 下载不存在对象返回 404"""
    response = await client.get("/storage/missing.txt", headers={"x-tenant": "acme"})

    assert response.status_code == 404
