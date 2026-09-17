"""缓存客户端 - https://valkey-py.readthedocs.io/en/latest/examples/asyncio_examples.html

客户端为惰性连接 命令均为协程 用完 await aclose() 关闭内部连接池
键前缀与超时在装配时收敛 供 api 与 worker 复用
"""

from typing import Final

import valkey.asyncio as valkey

# 默认键前缀
DEFAULT_PREFIX: Final[str] = "app"

# 默认超时秒数
DEFAULT_TIMEOUT: Final[float] = 5.0


class CacheClient:
    """带键前缀的异步缓存客户端"""

    def __init__(self, client: valkey.Valkey, prefix: str = DEFAULT_PREFIX) -> None:
        # 底层客户端
        self._client = client
        # 键前缀
        self._prefix = prefix

    def _key(self, key: str) -> str:
        """前缀键 {prefix}:{key}"""
        return f"{self._prefix}:{key}"

    async def get(self, key: str) -> str | None:
        """读取 键不存在返回 None"""
        return await self._client.get(self._key(key))

    async def set(
        self,
        key: str,
        value: str,
        *,
        ex: int | None = None,
        nx: bool = False,
    ) -> bool:
        """写入 ex 为过期秒数 nx 仅当不存在时写入 返回是否成功"""
        return bool(await self._client.set(self._key(key), value, ex=ex, nx=nx))

    async def delete(self, key: str) -> int:
        """删除 返回删除键数"""
        return int(await self._client.delete(self._key(key)))

    async def getdel(self, key: str) -> str | None:
        """读取并删除 一次性消费"""
        return await self._client.getdel(self._key(key))

    async def aclose(self) -> None:
        """关闭底层客户端连接池"""
        await self._client.aclose()


def create_client(
    url: str,
    *,
    prefix: str = DEFAULT_PREFIX,
    timeout: float = DEFAULT_TIMEOUT,
) -> CacheClient:
    """创建带键前缀与超时的异步客户端 惰性连接"""
    return CacheClient(
        valkey.Valkey.from_url(
            url,
            socket_timeout=timeout,
            socket_connect_timeout=timeout,
            decode_responses=True,
        ),
        prefix,
    )
