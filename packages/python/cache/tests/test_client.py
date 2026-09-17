"""缓存客户端测试"""

from typing import TYPE_CHECKING, Any, cast

from app.cache import CacheClient, create_client
from app.cache.client import DEFAULT_TIMEOUT

if TYPE_CHECKING:
    # 异步客户端 仅注解使用
    import valkey.asyncio as valkey


class StubValkey:
    """异步客户端桩 记录调用 返回固定值"""

    def __init__(self) -> None:
        # 调用记录 (方法 位置参数 关键字参数)
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    async def get(self, key: str) -> str | None:
        """记录并返回固定值"""
        self.calls.append(("get", (key,), {}))
        return "v"

    async def set(
        self,
        key: str,
        value: str,
        *,
        ex: int | None = None,
        nx: bool = False,
    ) -> bool:
        """记录并返回写入结果 nx 时返回 False"""
        self.calls.append(("set", (key, value), {"ex": ex, "nx": nx}))
        return not nx

    async def delete(self, key: str) -> int:
        """记录并返回删除键数"""
        self.calls.append(("delete", (key,), {}))
        return 1

    async def getdel(self, key: str) -> str | None:
        """记录并返回一次性读取值"""
        self.calls.append(("getdel", (key,), {}))
        return "t"

    async def aclose(self) -> None:
        """记录关闭"""
        self.calls.append(("aclose", (), {}))


def make_client() -> CacheClient:
    """桩客户端替代真实客户端 键前缀 app"""
    return CacheClient(cast("valkey.Valkey", StubValkey()), "app")


def test_create_client() -> None:
    """工厂创建缓存客户端 超时与响应解码写入连接参数"""
    client = create_client("valkey://localhost:6379/0")

    assert isinstance(client, CacheClient)
    kwargs = client._client.connection_pool.connection_kwargs
    assert kwargs["socket_timeout"] == DEFAULT_TIMEOUT
    assert kwargs["socket_connect_timeout"] == DEFAULT_TIMEOUT
    assert kwargs["decode_responses"] is True


def test_create_client_custom_timeout() -> None:
    """工厂可自定义超时"""
    client = create_client("valkey://localhost:6379/0", timeout=2.5)

    kwargs = client._client.connection_pool.connection_kwargs
    assert kwargs["socket_timeout"] == 2.5
    assert kwargs["socket_connect_timeout"] == 2.5


async def test_get_uses_prefixed_key() -> None:
    """读取使用前缀键并透传返回值"""
    stub = StubValkey()
    client = CacheClient(cast("valkey.Valkey", stub), "app")
    value = await client.get("a")

    assert value == "v"
    assert stub.calls == [("get", ("app:a",), {})]


async def test_set_passthrough() -> None:
    """写入透传 ex 与 nx 并返回写入结果"""
    stub = StubValkey()
    client = CacheClient(cast("valkey.Valkey", stub), "app")
    ok = await client.set("k", "v", ex=30, nx=True)

    assert ok is False
    assert stub.calls == [("set", ("app:k", "v"), {"ex": 30, "nx": True})]


async def test_set_default() -> None:
    """默认写入无过期且无条件"""
    stub = StubValkey()
    client = CacheClient(cast("valkey.Valkey", stub), "app")
    ok = await client.set("k", "v")

    assert ok is True
    assert stub.calls == [("set", ("app:k", "v"), {"ex": None, "nx": False})]


async def test_delete_uses_prefixed_key() -> None:
    """删除使用前缀键并返回删除键数"""
    stub = StubValkey()
    client = CacheClient(cast("valkey.Valkey", stub), "app")
    count = await client.delete("k")

    assert count == 1
    assert stub.calls == [("delete", ("app:k",), {})]


async def test_getdel_uses_prefixed_key() -> None:
    """一次性读取使用前缀键"""
    stub = StubValkey()
    client = CacheClient(cast("valkey.Valkey", stub), "app")
    value = await client.getdel("k")

    assert value == "t"
    assert stub.calls == [("getdel", ("app:k",), {})]


async def test_aclose() -> None:
    """关闭透传至底层客户端"""
    stub = StubValkey()
    client = CacheClient(cast("valkey.Valkey", stub), "app")
    await client.aclose()

    assert stub.calls == [("aclose", (), {})]
