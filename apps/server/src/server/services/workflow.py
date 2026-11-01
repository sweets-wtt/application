"""工作流服务"""

from typing import TYPE_CHECKING

from app.contracts.generated.http import RequestInput
from app.log import get_logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from server.core.constants import WORKFLOW_NAME

if TYPE_CHECKING:
    from hatchet_sdk import Hatchet

# 结构化日志器
logger = get_logger(__name__)

# Hatchet 状态 -> 契约枚举
_STATUS_MAP = {
    "QUEUED": "submitted",
    "RUNNING": "running",
    "COMPLETED": "succeeded",
    "FAILED": "failed",
    "CANCELLED": "failed",
}


async def submit(
    client: "Hatchet",
    session: AsyncSession,
    key: str,
    payload: RequestInput,
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
    workflow = client.workflow(name=WORKFLOW_NAME, input_validator=RequestInput)
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
    """查询 run 状态 - 本地幂等记录 + Hatchet 远端状态

    未记录的 run 返回 None; Hatchet 查询失败降级为 submitted(本地已受理)
    """
    result = await session.execute(
        text("SELECT run_id FROM idempotency WHERE run_id = :run_id"),
        {"run_id": run_id},
    )
    if result.first() is None:
        return None

    try:
        status = await client.runs.aio_get_status(run_id)
    except Exception:
        logger.warning("workflow.status_query_failed", run_id=run_id, exc_info=True)
        return "submitted"

    return _STATUS_MAP.get(str(getattr(status, "value", status)), "submitted")
