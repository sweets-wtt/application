"""缓存测试"""

import pytest
from app.cache import CacheClient
from server.adapters.cache import AuthzCache, LocalStore


class FakeBackend:
    """内存后端"""

    def __init__(self) -> None:
        self.data: dict[str, object] = {}
        self.set_calls: list[tuple[str, object, dict[str, object]]] = []
        self.closed = False
        self.failed = False

    async def get(self, key: str) -> object | None:
        """读取"""
        if self.failed:
            raise ConnectionError("缓存不可用")
        return self.data.get(key)

    async def set(self, key: str, value: object, **kwargs: object) -> object:
        """写入并记录调用"""
        if self.failed:
            raise ConnectionError("缓存不可用")
        self.set_calls.append((key, value, kwargs))
        self.data[key] = value
        return True

    async def aclose(self) -> None:
        """标记关闭"""
        self.closed = True


@pytest.fixture
def pair() -> tuple[AuthzCache, FakeBackend]:
    """缓存与后端"""
    backend = FakeBackend()
    timeout = 60
    cache = AuthzCache(CacheClient(backend, "authz:", timeout), LocalStore(), timeout)
    return cache, backend


async def test_set_get_roundtrip(pair: tuple[AuthzCache, FakeBackend]) -> None:
    """读写往返与键前缀、超时透传"""
    cache, backend = pair
    await cache.set("subject:1", "allow")
    assert await cache.get("subject:1") == "allow"

    key, value, kwargs = backend.set_calls[0]
    assert key == "authz:subject:1"
    assert value == "allow"
    assert kwargs == {"ex": 60}


async def test_get_decodes_bytes(pair: tuple[AuthzCache, FakeBackend]) -> None:
    """远端字节值解码"""
    cache, backend = pair
    backend.data["authz:k"] = b"raw"
    assert await cache.get("k") == "raw"


async def test_get_miss_returns_none(pair: tuple[AuthzCache, FakeBackend]) -> None:
    """远端权威 - 远端无值返回 None、本地有值也不越权"""
    cache, backend = pair
    await cache.set("k", "v")
    backend.data.clear()
    assert await cache.get("k") is None


async def test_fallback_local_when_down(pair: tuple[AuthzCache, FakeBackend]) -> None:
    """远端故障回退本地"""
    cache, backend = pair
    await cache.set("k", "v")
    backend.failed = True
    assert await cache.get("k") == "v"


async def test_down_empty_returns_none(pair: tuple[AuthzCache, FakeBackend]) -> None:
    """远端故障且本地无值返回 None - 不扩大权限"""
    cache, backend = pair
    backend.failed = True
    assert await cache.get("missing") is None


async def test_set_when_down_keeps_local(pair: tuple[AuthzCache, FakeBackend]) -> None:
    """远端故障时写入仍落本地"""
    cache, backend = pair
    backend.failed = True
    await cache.set("k", "v")
    assert await cache.get("k") == "v"


def test_local_store_expires() -> None:
    """本地存储惰性过期"""
    local = LocalStore()
    local.set("k", "v", 0)
    assert local.get("k") is None


async def test_close_closes_backend(pair: tuple[AuthzCache, FakeBackend]) -> None:
    """关闭透传"""
    cache, backend = pair
    await cache.close()
    assert backend.closed is True
