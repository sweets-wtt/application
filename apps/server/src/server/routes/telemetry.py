"""遥测路由"""

from typing import Any

from app.contracts.generated.http import TelemetryEventsRequest
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import model_validator

from server.services import telemetry as telemetry_service

# 请求体上限字节
BODY_LIMIT = 64 * 1024

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


async def body_limit(request: Request) -> None:
    """请求体上限 Content-Length 缺失或非法按超限处理"""
    length = request.headers.get("content-length")
    try:
        over = length is None or int(length) > BODY_LIMIT
    except ValueError:
        over = True
    if over:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail="请求体超限"
        )


# 遥测请求体 时间戳仅接受契约字符串 拒绝整数时间戳等隐式转换
class TelemetryEventsBody(TelemetryEventsRequest):
    """遥测请求体"""

    # 模型级校验 事件时间戳必须为字符串
    @model_validator(mode="before")
    @classmethod
    def _timestamps_must_be_str(cls, data: Any) -> Any:
        """事件时间戳仅接受字符串"""
        if isinstance(data, dict):
            for event in data.get("events") or []:
                if isinstance(event, dict) and not isinstance(
                    event.get("timestamp"), str
                ):
                    raise ValueError("timestamp 必须为字符串")
        return data


@router.post(
    path="/events",
    description="接收客户端批量遥测事件",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(body_limit)],
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "请求体无法解析"},
        status.HTTP_413_CONTENT_TOO_LARGE: {"description": "请求体超限"},
    },
)
async def create_events(body: TelemetryEventsBody) -> dict:
    """接收客户端批量遥测事件 逐条写出"""
    accepted = telemetry_service.record_events(body.service, body.release, body.events)
    return {"code": 0, "message": "ok", "data": {"accepted": accepted}}
