"""缓存适配器

进程级客户端惰性连接 api 每请求与 worker Task 共用
授权缓存只承载短期非敏感数据 未命中即未授权 不扩大权限
"""

import time
from typing import Final

from app.cache import CacheClient, create_client
from valkey.exceptions import ConnectionError as ValkeyConnectionError

from server.core.settings import cache_settings

# 本地回退上限
LOCAL_CACHE_MAX: Final[int] = 1024

# 进程级客户端 惰性连接 api 每请求与 worker Task 共用
client: CacheClient = create_client(cache_settings.cache.url)

# 本地回退缓存 键到 过期时刻与值 的映射
_local: dict[str, tuple[float, str]] = {}


async def get_cache() -> CacheClient:
    """每请求缓存客户端 依赖注入共用单例"""
    return client


def _local_get(key: str) -> str | None:
    """本地读取 过期即删"""
    entry = _local.get(key)
    if entry is None:
        return None
    expires, value = entry
    if expires <= time.monotonic():
        _local.pop(key, None)
        return None
    return value


def _local_set(key: str, value: str, ex: int) -> None:
    """本地写入 超上限淘汰最早过期项"""
    if len(_local) >= LOCAL_CACHE_MAX:
        _local.pop(min(_local, key=lambda k: _local[k][0]))
    _local[key] = (time.monotonic() + ex, value)


async def cache_get(cache: CacheClient, key: str) -> str | None:
    """授权缓存读取 远端不可用回退本地 未命中即未授权"""
    try:
        return await cache.get(key)
    except (ValkeyConnectionError, TimeoutError):
        return _local_get(key)


async def cache_set(cache: CacheClient, key: str, value: str, *, ex: int) -> bool:
    """授权缓存写入 远端不可用回退本地"""
    try:
        return await cache.set(key, value, ex=ex)
    except (ValkeyConnectionError, TimeoutError):
        _local_set(key, value, ex)
        return True
