"""实时路由"""

import json
import time
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, WebSocket
from starlette.websockets import WebSocketDisconnect
from valkey.exceptions import ValkeyError

from server.adapters.realtime import TicketStore, bus, get_ticket_store
from server.core.constants import TICKET_TTL_SECONDS, MessageType, WsCloseCode
from server.core.settings import settings
from server.services import realtime as realtime_service

router = APIRouter(prefix="/realtime", tags=["realtime"])


def origin_allowed(origin: str | None) -> bool:
    """来源允许 - 无来源放行、带来源必须命中允许列表"""
    return origin is None or origin in settings.realtime.origins


@router.post("/ticket", description="签发一次性票据")
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


@router.websocket("/ws")
async def realtime_ws(
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
    connection = realtime_service.Connection(websocket.send_text)
    realtime_service.hub.connect(connection)

    try:
        # 就绪事件
        connection.enqueue(
            realtime_service.build_event(MessageType.SYSTEM, {"status": "connected"})
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
                realtime_service.hub.subscribe(connection, topic)

            elif msg_type == MessageType.UNSUBSCRIBE:
                realtime_service.hub.unsubscribe(connection, topic)

            elif msg_type == MessageType.PUBLISH:
                # 发布到总线, 由总线分发给所有实例的订阅者
                payload = envelope.get("payload")
                event = realtime_service.build_event(
                    topic,
                    payload if isinstance(payload, dict) else {"data": payload},
                )
                await bus.publish(topic, event)

    except WebSocketDisconnect:
        pass
    finally:
        realtime_service.hub.disconnect(connection)
