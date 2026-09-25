"""缓存客户端测试"""

from app.cache.client import CacheClient


class FakeValkey:
    """记录调用参数的桩客户端"""

    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []

    async def get(self, key: str) -> str:
        self.calls.append(("get", (key,), {}))
        return "v"

    async def set(self, key: str, value: str, **kwargs: object) -> bool:
        self.calls.append(("set", (key, value), kwargs))
        return True

    async def aclose(self) -> None:
        self.calls.append(("aclose", (), {}))


def test_key_prefix() -> None:
    """键拼接前缀"""
    client = CacheClient(FakeValkey(), "app:", 60)

    assert client.key("user") == "app:user"


async def test_get_uses_prefix() -> None:
    """读取使用带前缀的键"""
    fake = FakeValkey()
    client = CacheClient(fake, "app:", 60)

    await client.get("user")

    assert fake.calls == [("get", ("app:user",), {})]


async def test_set_applies_prefix_and_timeout() -> None:
    """写入使用带前缀的键并附超时"""
    fake = FakeValkey()
    client = CacheClient(fake, "app:", 300)

    await client.set("token", "abc")

    assert fake.calls == [("set", ("app:token", "abc"), {"ex": 300})]


async def test_close_closes_underlying_client() -> None:
    """关闭透传底层客户端"""
    fake = FakeValkey()
    client = CacheClient(fake, "app:", 60)

    await client.close()

    assert fake.calls == [("aclose", (), {})]
