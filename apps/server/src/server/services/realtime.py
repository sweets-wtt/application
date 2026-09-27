"""实时服务"""

import json
from collections import deque
from collections.abc import Awaitable, Callable

from server.core.constants import REALTIME_QUEUE_LIMIT, MessageType


def build_event(topic: str, payload: dict) -> str:
    """实时事件 JSON 信封"""
    return json.dumps({"type": MessageType.EVENT, "topic": topic, "payload": payload})


class Connection:
    """单连接出站有界队列 - 满丢最旧"""

    def __init__(self, send: Callable[[str], Awaitable[None]]) -> None:
        self._send = send
        self._queue: deque[str] = deque(maxlen=REALTIME_QUEUE_LIMIT)

    @property
    def pending(self) -> int:
        """待发送条数"""
        return len(self._queue)

    def enqueue(self, event: str) -> None:
        """入队 - 满丢最旧"""
        self._queue.append(event)

    async def flush(self) -> None:
        """冲刷队列"""
        while self._queue:
            await self._send(self._queue.popleft())


class Hub:
    """连接集合、topic 订阅与事件分发"""

    def __init__(self) -> None:
        self._connections: set[Connection] = set()
        # 连接 -> 订阅主题集合
        self._subscriptions: dict[Connection, set[str]] = {}
        # 主题 -> 订阅连接集合
        self._topics: dict[str, set[Connection]] = {}

    def connect(self, connection: Connection) -> None:
        """登记连接"""
        self._connections.add(connection)
        self._subscriptions[connection] = set()

    def disconnect(self, connection: Connection) -> None:
        """摘除连接并清理订阅"""
        self._connections.discard(connection)
        topics = self._subscriptions.pop(connection, set())
        for topic in topics:
            subscribers = self._topics.get(topic)
            if subscribers is None:
                continue
            subscribers.discard(connection)
            if not subscribers:
                del self._topics[topic]

    @property
    def size(self) -> int:
        """登记连接数"""
        return len(self._connections)

    def subscribe(self, connection: Connection, topic: str) -> None:
        """订阅主题"""
        self._subscriptions.setdefault(connection, set()).add(topic)
        self._topics.setdefault(topic, set()).add(connection)

    def unsubscribe(self, connection: Connection, topic: str) -> None:
        """取消订阅主题"""
        topics = self._subscriptions.get(connection)
        if topics is not None:
            topics.discard(topic)
        subscribers = self._topics.get(topic)
        if subscribers is not None:
            subscribers.discard(connection)
            if not subscribers:
                del self._topics[topic]

    async def _deliver(self, connection: Connection, event: str) -> None:
        """向单连接投递事件 - 入队冲刷、失败摘除"""
        connection.enqueue(event)
        try:
            await connection.flush()
        except Exception:
            self.disconnect(connection)

    async def broadcast_to(self, topic: str, event: str) -> None:
        """向主题订阅者分发事件 - 失败摘除"""
        subscribers = self._topics.get(topic)
        if subscribers is None:
            return
        for connection in tuple(subscribers):
            await self._deliver(connection, event)

    async def broadcast(self, event: str) -> None:
        """广播全部连接 - 各连接入队并冲刷、失败摘除"""
        for connection in tuple(self._connections):
            await self._deliver(connection, event)


# 应用级连接中心
hub = Hub()
