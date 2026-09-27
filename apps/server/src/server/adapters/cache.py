"""缓存适配器"""

import time
from collections.abc import AsyncIterator
from contextlib import suppress

from app.cache import CacheClient, create_client

from server.core.settings import settings


class LocalStore:
    """进程内本地回退存储"""

    def __init__(self) -> None:
        self._entries: dict[str, tuple[float, str]] = {}

    def get(self, name: str) -> str | None:
        """读取 - 惰性过期"""
        entry = self._entries.get(name)
        if entry is None:
            return None

        expires, value = entry
        if time.monotonic() >= expires:
            # 过期即清除
            del self._entries[name]
            return None

        return value

    def set(self, name: str, value: str, timeout: int) -> None:
        """写入"""
        self._entries[name] = (time.monotonic() + timeout, value)


class AuthzCache:
    """短期非敏感授权缓存 - 远端优先、不可用回退本地、不扩大权限"""

    def __init__(self, client: CacheClient, local: LocalStore, timeout: int) -> None:
        self._client = client
        self._local = local
        self._timeout = timeout

    async def get(self, name: str) -> str | None:
        """读取 - 远端故障回退本地、无值返回 None"""
        try:
            value = await self._client.get(name)
        except Exception:
            return self._local.get(name)

        if value is None:
            return None

        if isinstance(value, bytes):
            return value.decode("utf-8")

        return str(value)

    async def set(self, name: str, value: str) -> None:
        """写入 - 本地必存、远端尽力而为"""
        self._local.set(name, value, self._timeout)

        with suppress(Exception):
            await self._client.set(name, value)

    async def close(self) -> None:
        """关闭连接"""
        await self._client.close()


# 进程级回退存储
_local = LocalStore()


async def get_authz_cache() -> AsyncIterator[AuthzCache]:
    """每请求生命周期的授权缓存"""
    cache = AuthzCache(
        create_client(
            url=settings.cache.url,
            key_prefix=settings.cache.key_prefix,
            timeout=settings.cache.timeout,
        ),
        _local,
        settings.cache.timeout,
    )

    yield cache

    await cache.close()
