"""业务服务 - 实时、遥测、对象存储与工作流"""

import asyncio
import json
from collections import deque
from collections.abc import AsyncIterator, Awaitable, Callable
from time import monotonic
from typing import Any, Final

from aiobotocore.client import AioBaseClient
from app.contracts.generated.http import TelemetryBatch, WorkflowInput
from app.data import Idempotency
from app.log import get_logger
from app.workflow import WorkflowClient
from botocore.exceptions import ClientError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.adapters import tenant_key
from server.core import (
    LEVEL_LOG_METHODS,
    MAX_UPLOAD_SIZE,
    REALTIME_QUEUE_LIMIT,
    WORKFLOW_NAME,
    MessageType,
    TelemetryLevel,
    settings,
)
from server.workflows import process as workflow_process

# 结构化日志器
logger = get_logger(__name__)


# ── 实时 ─────────────────────────


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
        """取消订阅"""
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


# ── 遥测 ─────────────────────────


async def ingest(payload: TelemetryBatch) -> int:
    """逐条结构化写出遥测事件 - 返回受理条数"""
    for event in payload.events:
        level = TelemetryLevel(event.level)
        method = getattr(logger, LEVEL_LOG_METHODS[level])
        method(
            "telemetry.event",
            service=payload.service,
            release=payload.release,
            level=event.level,
            fingerprint=event.fingerprint,
            message=event.message,
            timestamp=event.timestamp,
            context=event.context,
        )

    return len(payload.events)


# ── 对象存储 ─────────────────────────


class UploadTooLarge(ValueError):
    """对象上传超过上限"""


class NotFound(KeyError):
    """对象不存在"""


async def upload(
    client: AioBaseClient,
    tenant: str,
    key: str,
    stream: AsyncIterator[bytes],
) -> int:
    """流式上传对象并返回字节数。超过上限抛出 UploadTooLarge"""
    buffer = bytearray()

    # 分块累积 - 超限中止
    async for chunk in stream:
        if len(buffer) + len(chunk) > MAX_UPLOAD_SIZE:
            raise UploadTooLarge(f"上传超过 {MAX_UPLOAD_SIZE // (1024 * 1024)} MiB")
        buffer.extend(chunk)

    data = bytes(buffer)

    # 键带租户前缀写入
    await client.put_object(
        Bucket=settings.storage.bucket,
        Key=tenant_key(tenant, key),
        Body=data,
    )

    return len(data)


async def download(
    client: AioBaseClient,
    tenant: str,
    key: str,
) -> AsyncIterator[bytes]:
    """产出对象流。对象不存在抛出 NotFound"""
    try:
        result = await client.get_object(
            Bucket=settings.storage.bucket,
            Key=tenant_key(tenant, key),
        )
    except ClientError as exc:
        # 未找到键转领域异常、其余上抛
        if exc.response.get("Error", {}).get("Code") in {"NoSuchKey", "NotFound"}:
            raise NotFound(key) from exc
        raise

    body = result["Body"]

    return body.iter_chunks()


# ── 工作流 ─────────────────────────

# 状态查询超时 - 避免远端 RPC 阻塞请求
_QUERY_TIMEOUT_SECONDS: Final[float] = 3.0

# 非终态缓存 TTL - 减少重复 RPC
_PENDING_TTL_SECONDS: Final[float] = 5.0

# 终态集合 - 结果不再变化, 常驻缓存
_TERMINAL_STATUSES: Final[frozenset[str]] = frozenset({"succeeded", "failed"})

# DBOS 状态 -> 契约枚举
_STATUS_MAP = {
    "ENQUEUED": "submitted",
    "DELAYED": "submitted",
    "PENDING": "running",
    "SUCCESS": "succeeded",
    "ERROR": "failed",
    "MAX_RECOVERY_ATTEMPTS_EXCEEDED": "failed",
    "CANCELLED": "failed",
}

# 进程级状态缓存 - run_id -> (过期时刻 monotonic, 映射状态)
# 过期时刻为 None 表示终态, 常驻缓存
_status_cache: dict[str, tuple[float | None, str]] = {}


def _map_status(status: Any) -> str:
    """DBOS 状态对象 -> 契约枚举"""
    return _STATUS_MAP.get(str(getattr(status, "status", status)), "submitted")


async def submit(
    client: WorkflowClient,
    session: AsyncSession,
    key: str,
    payload: WorkflowInput,
) -> str:
    """提交工作流 run - 幂等同事务

    已有 Idempotency-Key 则返回已记录 run_id;否则触发 run 并同事务记录
    """
    # 幂等查询 - 已有则直接返回
    existing = await session.scalar(
        select(Idempotency.run_id).where(Idempotency.key == key)
    )
    if existing is not None:
        return existing

    # 触发工作流 - 以幂等键为 workflow_id, DBOS 自身亦去重
    run_id = client.start(workflow_process, payload, key)

    # 同事务记录幂等键
    session.add(Idempotency(key=key, workflow_name=WORKFLOW_NAME, run_id=run_id))
    await session.commit()

    return run_id


async def get_status(
    client: WorkflowClient,
    session: AsyncSession,
    run_id: str,
) -> str | None:
    """查询 run 状态 - 本地幂等记录 + 缓存 + DBOS 远端状态

    未记录的 run 返回 None; 终态常驻缓存; 非终态短 TTL 缓存;
    DBOS 查询失败/超时降级为 submitted(本地已受理)且不写缓存
    """
    result = await session.scalar(
        select(Idempotency.run_id).where(Idempotency.run_id == run_id)
    )
    if result is None:
        return None

    # 命中缓存 - 终态常驻; 非终态未过期直接返回
    cached = _status_cache.get(run_id)
    if cached is not None:
        expires_at, cached_status = cached
        if expires_at is None or expires_at > monotonic():
            return cached_status

    try:
        # DBOS 查询为同步调用 - 移出事件循环并加超时
        status = await asyncio.wait_for(
            asyncio.to_thread(client.status, run_id),
            timeout=_QUERY_TIMEOUT_SECONDS,
        )
    except Exception:
        # 降级不写缓存 - 下次请求可重试
        _status_cache.pop(run_id, None)
        logger.warning("workflow.status_query_failed", run_id=run_id, exc_info=True)
        return "submitted"

    mapped = _map_status(status)
    if mapped in _TERMINAL_STATUSES:
        _status_cache[run_id] = (None, mapped)
    else:
        _status_cache[run_id] = (monotonic() + _PENDING_TTL_SECONDS, mapped)

    return mapped
