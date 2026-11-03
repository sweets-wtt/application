"""HTTP 路由 - 全部端点"""

from typing import Annotated

import fastapi
from app.contracts.generated.http import TelemetryBatch, WorkflowInput
from app.workflow import WorkflowClient
from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Request,
)

from server import services
from server.adapters import get_workflow_client
from server.auth import require_permission
from server.core import MAX_TELEMETRY_BODY_BYTES
from server.limits import DEFAULT_LIMIT, WORKFLOW_LIMIT, limiter

# 存活探针
healthz_router = APIRouter(tags=["health"])

# 遥测
telemetry_router = APIRouter(tags=["telemetry"])

# 工作流
workflow_router = APIRouter(prefix="/workflow", tags=["workflow"])


@healthz_router.get(path="/healthz", description="存活探针")
@limiter.limit(DEFAULT_LIMIT)
async def get_healthz(request: Request) -> dict:
    """存活探针 - 返回 ok"""
    return {"code": 0, "message": "ok", "data": {"status": "ok"}}


@telemetry_router.post(
    path="/telemetry/events",
    status_code=202,
    description="批量接收前端遥测事件",
    dependencies=[Depends(require_permission("telemetry:write"))],
)
@limiter.limit(DEFAULT_LIMIT)
async def ingest_telemetry(request: Request, payload: TelemetryBatch) -> dict:
    """批量接收前端遥测事件 - 超限返回 413"""
    # 请求体超限 - 413 - 缺失长度时跳过、由后续读取环节兜底
    length = request.headers.get("content-length", "")
    if length.isdigit() and int(length) > MAX_TELEMETRY_BODY_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"请求体超过 {MAX_TELEMETRY_BODY_BYTES // 1024} KiB",
        )

    accepted = await services.ingest(payload)

    return {"code": 0, "message": "ok", "data": {"accepted": accepted}}


@workflow_router.post(
    path="/runs",
    status_code=202,
    description="提交工作流 run",
    dependencies=[Depends(require_permission("workflow:write"))],
)
@limiter.limit(WORKFLOW_LIMIT)
async def create_workflow_run(
    request: Request,
    payload: WorkflowInput,
    idempotency_key: Annotated[
        str, Header(alias="Idempotency-Key", description="幂等键")
    ],
    client: Annotated[WorkflowClient, Depends(get_workflow_client)],
) -> dict:
    """提交工作流 run - 以幂等键为 workflow_id 去重"""
    run_id = await services.submit(client, idempotency_key, payload)

    return {
        "code": 0,
        "message": "ok",
        "data": {"run_id": run_id, "status": "submitted"},
    }


@workflow_router.get(
    path="/runs/{run_id}",
    description="查询工作流 run",
    dependencies=[Depends(require_permission("workflow:read"))],
)
@limiter.limit(DEFAULT_LIMIT)
async def get_workflow_run(
    request: Request,
    run_id: str,
    client: Annotated[WorkflowClient, Depends(get_workflow_client)],
) -> dict:
    """查询工作流 run - 不存在返回 404"""
    status = await services.get_status(client, run_id)
    if status is None:
        raise HTTPException(status_code=404, detail="run 不存在")

    return {"code": 0, "message": "ok", "data": {"run_id": run_id, "status": status}}


def include_routes(app: fastapi.FastAPI) -> None:
    """注册全部路由"""
    app.include_router(healthz_router)
    app.include_router(telemetry_router)
    app.include_router(workflow_router)
