"""业务服务 - 遥测与工作流"""

import asyncio
from time import monotonic
from typing import Any, Final

from app.contracts.generated.http import TelemetryBatch, WorkflowInput
from app.log import get_logger
from app.workflow import WorkflowClient

from server.core import LEVEL_LOG_METHODS, TelemetryLevel
from server.workflows import process as workflow_process

# 结构化日志器
logger = get_logger(__name__)


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
    key: str,
    payload: WorkflowInput,
) -> str:
    """提交工作流 run - 以幂等键为 workflow_id

    DBOS 按 workflow_id 自身去重, 同键不会重复执行
    """
    # DBOS 启动为同步调用, 移出事件循环避免并发提交时串行阻塞
    return await asyncio.to_thread(client.start, workflow_process, payload, key)


async def get_status(
    client: WorkflowClient,
    run_id: str,
) -> str | None:
    """查询 run 状态 - 缓存 + DBOS 远端状态

    远端无记录返回 None; 终态常驻缓存; 非终态短 TTL 缓存;
    DBOS 查询失败/超时降级为 submitted 且不写缓存
    """
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

    if status is None:
        # 远端无此 run
        return None

    mapped = _map_status(status)
    if mapped in _TERMINAL_STATUSES:
        _status_cache[run_id] = (None, mapped)
    else:
        _status_cache[run_id] = (monotonic() + _PENDING_TTL_SECONDS, mapped)

    return mapped
