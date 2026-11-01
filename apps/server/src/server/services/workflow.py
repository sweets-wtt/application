"""工作流服务"""

import asyncio
from time import monotonic
from typing import TYPE_CHECKING, Any, Final

from app.contracts.generated.http import WorkflowInput
from app.log import get_logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from server.core.constants import WORKFLOW_NAME

if TYPE_CHECKING:
    from hatchet_sdk import Hatchet

# 结构化日志器
logger = get_logger(__name__)

# 状态查询超时 - 避免远端 RPC 阻塞请求
_QUERY_TIMEOUT_SECONDS: Final[float] = 3.0

# 非终态缓存 TTL - 减少重复 RPC
_PENDING_TTL_SECONDS: Final[float] = 5.0

# 终态集合 - 结果不再变化, 常驻缓存
_TERMINAL_STATUSES: Final[frozenset[str]] = frozenset({"succeeded", "failed"})

# Hatchet 状态 -> 契约枚举
_STATUS_MAP = {
    "QUEUED": "submitted",
    "RUNNING": "running",
    "COMPLETED": "succeeded",
    "FAILED": "failed",
    "CANCELLED": "failed",
}

# 进程级状态缓存 - run_id -> (过期时刻 monotonic, 映射状态)
# 过期时刻为 None 表示终态, 常驻缓存
_status_cache: dict[str, tuple[float | None, str]] = {}


def _map_status(status: Any) -> str:
    """Hatchet 状态对象/字符串 -> 契约枚举"""
    return _STATUS_MAP.get(str(getattr(status, "value", status)), "submitted")


async def submit(
    client: "Hatchet",
    session: AsyncSession,
    key: str,
    payload: WorkflowInput,
) -> str:
    """提交工作流 run - 幂等同事务

    已有 Idempotency-Key 则返回已记录 run_id;否则触发 run 并同事务记录
    """
    # 幂等查询 - 已有则直接返回
    existing = await session.execute(
        text("SELECT run_id FROM idempotency WHERE key = :key"),
        {"key": key},
    )
    row = existing.first()
    if row is not None:
        return row.run_id

    # 触发工作流 run - 不等待完成
    workflow = client.workflow(name=WORKFLOW_NAME, input_validator=WorkflowInput)
    run = await workflow.aio_run_no_wait(payload)

    # 同事务记录幂等键
    await session.execute(
        text(
            "INSERT INTO idempotency (key, workflow_name, run_id) "
            "VALUES (:key, :workflow, :run_id)"
        ),
        {"key": key, "workflow": WORKFLOW_NAME, "run_id": run.workflow_run_id},
    )
    await session.commit()

    return run.workflow_run_id


async def get_status(
    client: "Hatchet",
    session: AsyncSession,
    run_id: str,
) -> str | None:
    """查询 run 状态 - 本地幂等记录 + 缓存 + Hatchet 远端状态

    未记录的 run 返回 None; 终态常驻缓存, 非终态短 TTL 缓存;
    Hatchet 查询失败/超时降级为 submitted(本地已受理)且不写缓存
    """
    result = await session.execute(
        text("SELECT run_id FROM idempotency WHERE run_id = :run_id"),
        {"run_id": run_id},
    )
    if result.first() is None:
        return None

    # 命中缓存 - 终态常驻, 非终态未过期直接返回
    cached = _status_cache.get(run_id)
    if cached is not None:
        expires_at, cached_status = cached
        if expires_at is None or expires_at > monotonic():
            return cached_status

    try:
        status = await asyncio.wait_for(
            client.runs.aio_get_status(run_id),
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
