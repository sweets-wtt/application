"""缓存客户端"""

from typing import Any, Final, Protocol

from valkey.asyncio import Valkey

# 默认超时秒数
DEFAULT_TIMEOUT: Final[int] = 60


# 依赖注入协议
class Backend(Protocol):
    """缓存后端协议"""

    async def get(self, key: str) -> Any:
        """读取"""

    async def set(self, key: str, value: Any, **kwargs: Any) -> Any:
        """写入"""

    async def aclose(self) -> None:
        """关闭"""


class CacheClient:
    """带键前缀与超时的缓存客户端"""

    def __init__(self, client: Backend, key_prefix: str, timeout: int) -> None:
        self._client = client
        self._key_prefix = key_prefix
        self._timeout = timeout

    def key(self, name: str) -> str:
        """拼接带前缀的键"""
        return f"{self._key_prefix}{name}"

    async def get(self, name: str) -> Any:
        """读取"""
        return await self._client.get(self.key(name))

    async def set(self, name: str, value: Any) -> Any:
        """写入并附超时"""
        return await self._client.set(self.key(name), value, ex=self._timeout)

    async def close(self) -> None:
        """关闭连接"""
        await self._client.aclose()


def create_client(
    url: str, key_prefix: str, timeout: int = DEFAULT_TIMEOUT
) -> CacheClient:
    """创建缓存客户端"""
    return CacheClient(Valkey.from_url(url), key_prefix, timeout)
