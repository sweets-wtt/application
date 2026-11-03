"""HTTP 路由 - 全部端点"""

import json
import time
from typing import Annotated

import fastapi
from aiobotocore.client import AioBaseClient
from app.contracts.generated.http import TelemetryBatch, WorkflowInput
from app.workflow import WorkflowClient
from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
    WebSocket,
)
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse
from starlette.websockets import WebSocketDisconnect
from valkey.exceptions import ValkeyError

from server import services
from server.adapters import (
    TicketStore,
    bus,
    get_session,
    get_storage_client,
    get_ticket_store,
    get_workflow_client,
)
from server.core import (
    MAX_TELEMETRY_BODY_BYTES,
    TICKET_TTL_SECONDS,
    MessageType,
    WsCloseCode,
    settings,
)

# 存活探针
healthz_router = APIRouter(tags=["health"])

# 对象存储
storage_router = APIRouter(prefix="/storage", tags=["storage"])

# 实时
realtime_router = APIRouter(prefix="/realtime", tags=["realtime"])

# 遥测
telemetry_router = APIRouter(tags=["telemetry"])

# 工作流
workflow_router = APIRouter(prefix="/workflow", tags=["workflow"])


def origin_allowed(origin: str | None) -> bool:
    """来源允许 - 无来源放行、带来源必须命中允许列表"""
    return origin is None or origin in settings.realtime.origins


@healthz_router.get(path="/healthz", description="存活探针")
async def get_healthz() -> dict:
    """存活探针 - 返回 ok"""
    return {"code": 0, "message": "ok", "data": {"status": "ok"}}


@storage_router.put("/{key:path}", description="流式上传对象")
async def put_object(
    request: Request,
    key: str,
    x_tenant: Annotated[str, Header(description="租户标识")],
    client: Annotated[AioBaseClient, Depends(get_storage_client)],
) -> dict:
    """流式上传对象 - 超限返回 413"""
    # 流式读取请求体并计数
    try:
        size = await services.upload(client, x_tenant, key, request.stream())
    except services.UploadTooLarge:
        raise HTTPException(status_code=413, detail="上传超过 10 MiB") from None

    return {"code": 0, "message": "ok", "data": {"key": key, "size": size}}


@storage_router.get("/{key:path}", description="流式下载对象")
async def get_object(
    key: str,
    x_tenant: Annotated[str, Header(description="租户标识")],
    client: Annotated[AioBaseClient, Depends(get_storage_client)],
) -> Response:
    """流式下载对象 - 不存在返回 404"""
    try:
        stream = await services.download(client, x_tenant, key)
    except services.NotFound:
        raise HTTPException(status_code=404, detail="对象不存在") from None

    return StreamingResponse(stream, media_type="application/octet-stream")


@realtime_router.post("/ticket", description="签发一次性票据")
async def issue_ticket(
    store: Annotated[TicketStore, Depends(get_ticket_store)],
    origin: Annotated[str | None, Header(description="请求来源")] = None,
) -> dict:
    """签发一次性票据 - 来源校验"""
    if not origin_allowed(origin):
        raise HTTPException(status_code=403, detail="来源不在允许列表")

    try:
        ticket = await store.issue()
    except ValkeyError as exc:
        raise HTTPException(status_code=503, detail="实时票据存储不可用") from exc

    return {
        "code": 0,
        "message": "ok",
        "data": {
            "ticket": ticket,
            "expiresAtMs": int(time.time() * 1000) + TICKET_TTL_SECONDS * 1000,
        },
    }


@realtime_router.websocket("/ws")
async def connect_realtime(
    websocket: WebSocket,
    store: Annotated[TicketStore, Depends(get_ticket_store)],
    ticket: Annotated[str, Query(description="一次性票据")],
) -> None:
    """实时连接 - 来源校验与一次性票据"""
    origin = websocket.headers.get("origin")
    if not origin_allowed(origin):
        # 来源不允许
        await websocket.close(code=WsCloseCode.ORIGIN_DENIED)
        return

    try:
        consumed = await store.consume(ticket)
    except ValkeyError:
        # 票据存储不可用
        await websocket.close(code=WsCloseCode.TICKET_STORE_UNAVAILABLE)
        return

    if not consumed:
        # 票据无效
        await websocket.close(code=WsCloseCode.TICKET_INVALID)
        return

    await websocket.accept()
    connection = services.Connection(websocket.send_text)
    services.hub.connect(connection)

    try:
        # 就绪事件
        connection.enqueue(
            services.build_event(MessageType.SYSTEM, {"status": "connected"})
        )
        await connection.flush()

        # 消息循环
        while True:
            data = await websocket.receive_text()

            # 心跳
            if data == MessageType.PING:
                await websocket.send_text(MessageType.PONG)
                continue

            # 解析信封
            try:
                envelope = json.loads(data)
            except json.JSONDecodeError:
                continue

            msg_type = envelope.get("type")
            topic = envelope.get("topic")
            if not isinstance(topic, str) or not topic:
                continue

            if msg_type == MessageType.SUBSCRIBE:
                services.hub.subscribe(connection, topic)

            elif msg_type == MessageType.UNSUBSCRIBE:
                services.hub.unsubscribe(connection, topic)

            elif msg_type == MessageType.PUBLISH:
                # 发布到总线, 由总线分发给所有实例的订阅者
                payload = envelope.get("payload")
                event = services.build_event(
                    topic,
                    payload if isinstance(payload, dict) else {"data": payload},
                )
                await bus.publish(topic, event)

    except WebSocketDisconnect:
        pass
    finally:
        services.hub.disconnect(connection)


@telemetry_router.post(
    path="/telemetry/events", status_code=202, description="批量接收前端遥测事件"
)
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


@workflow_router.post(path="/runs", status_code=202, description="提交工作流 run")
async def create_workflow_run(
    payload: WorkflowInput,
    idempotency_key: Annotated[
        str, Header(alias="Idempotency-Key", description="幂等键")
    ],
    client: Annotated[WorkflowClient, Depends(get_workflow_client)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    """提交工作流 run - 幂等"""
    run_id = await services.submit(client, session, idempotency_key, payload)

    return {
        "code": 0,
        "message": "ok",
        "data": {"run_id": run_id, "status": "submitted"},
    }


@workflow_router.get(path="/runs/{run_id}", description="查询工作流 run")
async def get_workflow_run(
    run_id: str,
    client: Annotated[WorkflowClient, Depends(get_workflow_client)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    """查询工作流 run - 不存在返回 404"""
    status = await services.get_status(client, session, run_id)
    if status is None:
        raise HTTPException(status_code=404, detail="run 不存在")

    return {"code": 0, "message": "ok", "data": {"run_id": run_id, "status": status}}


def include_routes(app: fastapi.FastAPI) -> None:
    """注册全部路由"""
    app.include_router(healthz_router)
    app.include_router(storage_router)
    app.include_router(realtime_router)
    app.include_router(telemetry_router)
    app.include_router(workflow_router)
