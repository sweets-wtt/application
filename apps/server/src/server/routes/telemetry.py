"""遥测接收路由"""

from app.contracts.generated.http import TelemetryIngest
from fastapi import APIRouter, HTTPException, Request

from server.core.constants import MAX_TELEMETRY_BODY_BYTES
from server.services import telemetry as telemetry_service

router = APIRouter(tags=["telemetry"])


@router.post(
    path="/telemetry/events", status_code=202, description="批量接收前端遥测事件"
)
async def telemetry_events(request: Request, payload: TelemetryIngest) -> dict:
    """批量接收前端遥测事件 - 超限返回 413"""
    # 请求体超限 - 413 - 缺失长度时跳过、由后续读取环节兜底
    length = request.headers.get("content-length", "")
    if length.isdigit() and int(length) > MAX_TELEMETRY_BODY_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"请求体超过 {MAX_TELEMETRY_BODY_BYTES // 1024} KiB",
        )

    accepted = await telemetry_service.ingest(payload)

    return {"code": 0, "message": "ok", "data": {"accepted": accepted}}
