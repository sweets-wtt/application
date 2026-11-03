"""外部系统适配 - 缓存、数据库、实时、对象存储与工作流客户端"""

import asyncio
import secrets
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import suppress
from typing import Protocol

from aiobotocore.client import AioBaseClient
from app.data.cache import CacheClient
from app.data.cache import create_client as create_cache_client
from app.data.db import create_engine, create_session_factory
from app.data.storage import StorageSettings
from app.data.storage import create_client as create_storage_client
from app.workflow import WorkflowClient, WorkflowSettings
from app.workflow import create_client as create_workflow_client
from sqlalchemy.ext.asyncio import AsyncSession
from valkey.asyncio import Valkey

from server.core import (
    TICKET_ISSUE_ATTEMPTS,
    TICKET_TOKEN_BYTES,
    TICKET_TTL_SECONDS,
    settings,
)

# ── 缓存 ─────────────────────────


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
        create_cache_client(
            url=settings.cache.url,
            key_prefix=settings.cache.key_prefix,
            timeout=settings.cache.timeout,
        ),
        _local,
        settings.cache.timeout,
    )

    yield cache

    await cache.close()


# ── 数据库 ─────────────────────────

# 异步引擎 - PgBouncer 兼容默认值由 app-data 提供
engine = create_engine(settings.database.url)

# 会话工厂 - api 每请求 / worker 任务共用
session_factory = create_session_factory(engine)


async def get_session() -> AsyncIterator[AsyncSession]:
    """每请求生命周期的数据库会话"""
    async with session_factory() as session:
        yield session


# ── 实时 ─────────────────────────


class Backend(Protocol):
    """票据存储协议"""

    async def set(self, name: str, value: str, *, nx: bool, ex: int) -> object: ...

    async def getdel(self, name: str) -> object | None: ...

    async def aclose(self) -> None: ...


class TicketStore:
    """一次性票据存储 - 键即票据、SET NX EX 签发、GETDEL 消费"""

    def __init__(self, client: Backend, key_prefix: str) -> None:
        self._client = client
        self._key_prefix = key_prefix

    async def issue(self) -> str:
        """签发 256 bit 一次性票据"""
        for _ in range(TICKET_ISSUE_ATTEMPTS):
            ticket = secrets.token_urlsafe(TICKET_TOKEN_BYTES)

            stored = await self._client.set(
                self._key_prefix + ticket,
                "1",
                nx=True,
                ex=TICKET_TTL_SECONDS,
            )
            if stored:
                return ticket

        raise RuntimeError("票据签发碰撞")

    async def consume(self, ticket: str) -> bool:
        """消费票据 - 一次性、返回是否存在"""
        result = await self._client.getdel(self._key_prefix + ticket)

        return result is not None

    async def close(self) -> None:
        """关闭连接"""
        await self._client.aclose()


async def get_ticket_store() -> AsyncIterator[TicketStore]:
    """每请求生命周期的票据存储"""
    store = TicketStore(
        Valkey.from_url(settings.realtime.url),
        settings.realtime.ticket_prefix,
    )
    yield store
    await store.close()


class PubSubBus:
    """Valkey Pub/Sub 总线 - 跨实例消息中继

    通道命名: {prefix}{topic}, 订阅前缀通配以接收全部主题
    """

    def __init__(self, url: str, prefix: str) -> None:
        self._url = url
        self._prefix = prefix
        # 发布用独立连接
        self._publisher: Valkey | None = None
        # 订阅连接与监听任务
        self._pubsub = None
        self._listener: asyncio.Task[None] | None = None
        # 消息回调: (topic, message) -> Awaitable
        self._handler: Callable[[str, str], Awaitable[None]] | None = None

    def channel(self, topic: str) -> str:
        """主题对应的 Valkey 通道名"""
        return self._prefix + topic

    def topic_of(self, channel: str) -> str:
        """从通道名还原主题"""
        return channel.removeprefix(self._prefix)

    async def start(self, handler: Callable[[str, str], Awaitable[None]]) -> None:
        """启动监听 - 订阅前缀通配并转发到回调

        Valkey 不可用时降级为单实例模式 (仅本进程 Hub 内分发)。
        """
        self._handler = handler

        try:
            self._publisher = Valkey.from_url(self._url)

            client = Valkey.from_url(self._url)
            self._pubsub = client.pubsub()
            await self._pubsub.psubscribe(self._prefix + "*")

            self._listener = asyncio.create_task(self._listen())
        except Exception:
            # 总线不可用 - 降级为单实例模式
            self._publisher = None
            self._pubsub = None
            self._listener = None

    async def publish(self, topic: str, message: str) -> None:
        """发布消息到主题通道 - 总线未启动时降级为本进程分发"""
        if self._publisher is not None:
            await self._publisher.publish(self.channel(topic), message)
            return

        # 降级: 直接回调本进程 handler
        if self._handler is not None:
            await self._handler(topic, message)

    async def _listen(self) -> None:
        """监听循环 - 仅处理 message/pmessage"""
        if self._pubsub is None or self._handler is None:
            return

        try:
            async for message in self._pubsub.listen():
                msg_type = message.get("type")
                if msg_type not in ("message", "pmessage"):
                    continue
                channel = message.get("channel") or message.get("pattern")
                data = message.get("data")
                if channel is None or data is None:
                    continue
                if isinstance(channel, bytes):
                    channel = channel.decode("utf-8")
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                await self._handler(self.topic_of(channel), data)
        except asyncio.CancelledError:
            pass

    async def close(self) -> None:
        """关闭总线"""
        if self._listener is not None:
            self._listener.cancel()
            with suppress(Exception):
                await self._listener
            self._listener = None

        for client in (self._pubsub, self._publisher):
            if client is not None:
                await client.aclose()
        self._pubsub = None
        self._publisher = None


# 应用级总线
bus = PubSubBus(settings.realtime.url, settings.realtime.pubsub_prefix)


async def get_bus() -> PubSubBus:
    """获取应用级总线"""
    return bus


# ── 对象存储 ─────────────────────────

# 客户端装配参数
storage_settings = StorageSettings(
    endpoint_url=settings.storage.endpoint_url,
    access_key_id=settings.storage.access_key_id,
    secret_access_key=settings.storage.secret_access_key,
    region_name=settings.storage.region_name,
    bucket=settings.storage.bucket,
)


def tenant_key(tenant: str, key: str) -> str:
    """租户前缀对象键"""
    return f"{tenant}/{key}"


async def get_storage_client() -> AsyncIterator[AioBaseClient]:
    """每请求生命周期的存储客户端"""
    async with create_storage_client(storage_settings) as client:
        yield client


# ── 工作流 ─────────────────────────

# 客户端装配参数
workflow_settings = WorkflowSettings(
    system_database_url=settings.workflow.system_database_url,
    app_name=settings.workflow.app_name,
)

# 进程级客户端单例
_client: "WorkflowClient | None" = None


def get_workflow_client() -> "WorkflowClient":
    """提交侧 - 工作流客户端单例"""
    global _client

    if _client is None:
        _client = create_workflow_client(workflow_settings)
    return _client
