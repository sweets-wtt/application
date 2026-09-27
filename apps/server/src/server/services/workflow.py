"""工作流服务"""

from typing import TYPE_CHECKING

from app.contracts.generated.http import RequestInput
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from server.core.constants import WORKFLOW_NAME

if TYPE_CHECKING:
    from hatchet_sdk import Hatchet


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


async def get_status(session: AsyncSession, run_id: str) -> str | None:
    """查询 run 状态 - 基于本地幂等记录

    远端状态需对接 hatchet.runs,此处仅核验 run 是否已受理
    """
    result = await session.execute(
        text("SELECT run_id FROM idempotency WHERE run_id = :run_id"),
        {"run_id": run_id},
    )
    if result.first() is None:
        return None

    return "submitted"
