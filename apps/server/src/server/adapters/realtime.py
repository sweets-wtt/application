"""实时适配器"""

import asyncio
import secrets
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import suppress
from typing import Protocol

from valkey.asyncio import Valkey

from server.core.constants import (
    TICKET_ISSUE_ATTEMPTS,
    TICKET_TOKEN_BYTES,
    TICKET_TTL_SECONDS,
)
from server.core.settings import settings


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
        """消费票据 - 一次性、返回是否有效"""
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
    """Valkey Pub/Sub 总线 - 跨实例消息中转

    通道命名: {prefix}{topic}, 订阅前缀通配以接收全部主题.
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

        Valkey 不可用时降级为单实例模式 (仅本进程 Hub 内分发).
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
