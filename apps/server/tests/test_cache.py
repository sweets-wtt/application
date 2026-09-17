"""缓存适配器测试"""

from typing import TYPE_CHECKING, Any, cast

from app.cache import CacheClient
from server.adapters import cache
from valkey.exceptions import ConnectionError

if TYPE_CHECKING:
    # 异步客户端 仅注解使用
    import valkey.asyncio as valkey


class StubValkey:
    """异步客户端桩 可注入远端不可用"""

    def __init__(self, *, fail: bool = False) -> None:
        # 是否让远端不可用
        self.fail = fail
        # 调用记录 (方法 位置参数 关键字参数)
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    async def get(self, key: str) -> str | None:
        """记录并返回固定值 可注入失败"""
        self.calls.append(("get", (key,), {}))
        if self.fail:
            raise ConnectionError("远端不可用")
        return "v"

    async def set(
        self,
        key: str,
        value: str,
        *,
        ex: int | None = None,
        nx: bool = False,
    ) -> bool:
        """记录写入结果 可注入失败"""
        self.calls.append(("set", (key, value), {"ex": ex, "nx": nx}))
        if self.fail:
            raise ConnectionError("远端不可用")
        return True


def make_client(*, fail: bool = False) -> tuple[CacheClient, StubValkey]:
    """桩客户端与桩实例 类型对齐适配器入参"""
    stub = StubValkey(fail=fail)
    return CacheClient(cast("valkey.Valkey", stub), "app"), stub


async def test_get_cache_dependency() -> None:
    """依赖注入返回进程级共用单例 worker Task 复用同一入口"""
    dep = await cache.get_cache()

    assert dep is cache.client
    assert isinstance(dep, CacheClient)


async def test_get_passthrough() -> None:
    """远端可用时透传读取"""
    client, stub = make_client()
    value = await cache.cache_get(client, "k")

    assert value == "v"
    assert stub.calls == [("get", ("app:k",), {})]


async def test_set_passthrough() -> None:
    """远端可用时透传写入"""
    client, stub = make_client()
    ok = await cache.cache_set(client, "k", "v", ex=60)

    assert ok is True
    assert stub.calls == [("set", ("app:k", "v"), {"ex": 60, "nx": False})]


async def test_set_falls_back_to_local() -> None:
    """远端不可用写入回退本地 随后读取命中本地"""
    client, stub = make_client(fail=True)
    ok = await cache.cache_set(client, "k", "v", ex=60)

    assert ok is True
    assert stub.calls == [("set", ("app:k", "v"), {"ex": 60, "nx": False})]

    value = await cache.cache_get(client, "k")

    assert value == "v"


async def test_get_miss_without_fallback_value() -> None:
    """远端不可用且无本地值时未命中即未授权"""
    client, _ = make_client(fail=True)
    value = await cache.cache_get(client, "missing")

    assert value is None


async def test_local_expiry() -> None:
    """本地回退过期即删"""
    client, _ = make_client(fail=True)
    await cache.cache_set(client, "k", "v", ex=0)
    value = await cache.cache_get(client, "k")

    assert value is None


async def test_local_bounded() -> None:
    """本地回退超上限淘汰 不无界增长"""
    client, _ = make_client(fail=True)
    for index in range(cache.LOCAL_CACHE_MAX + 1):
        await cache.cache_set(client, f"k{index}", "v", ex=60)

    assert len(cache._local) == cache.LOCAL_CACHE_MAX
