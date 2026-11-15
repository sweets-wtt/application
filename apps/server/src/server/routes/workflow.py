"""工作流路由"""

from typing import Annotated

from app.contracts.generated.http import RequestInput
from fastapi import APIRouter, Depends, Header, HTTPException
from hatchet_sdk import Hatchet
from sqlalchemy.ext.asyncio import AsyncSession

from server.adapters.database import get_session
from server.adapters.workflow import get_client
from server.services import workflow as workflow_service

router = APIRouter(prefix="/workflow", tags=["workflow"])


@router.post(path="/runs", status_code=202, description="提交工作流 run")
async def submit_run(
    payload: RequestInput,
    idempotency_key: Annotated[
        str, Header(alias="Idempotency-Key", description="幂等键")
    ],
    client: Annotated[Hatchet, Depends(get_client)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    """提交工作流 run - 幂等"""
    run_id = await workflow_service.submit(client, session, idempotency_key, payload)

    return {
        "code": 0,
        "message": "ok",
        "data": {"run_id": run_id, "status": "submitted"},
    }


@router.get(path="/runs/{run_id}", description="查询工作流 run")
async def get_run(
    run_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    """查询工作流 run - 不存在返回 404"""
    status = await workflow_service.get_status(session, run_id)
    if status is None:
        raise HTTPException(status_code=404, detail="run 不存在")

    return {"code": 0, "message": "ok", "data": {"run_id": run_id, "status": status}}
