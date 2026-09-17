"""实时服务"""

import asyncio
from typing import Any, Final

from pydantic import BaseModel

# 队列上限
EVENT_QUEUE_MAX: Final[int] = 1024


class RealtimeEvent(BaseModel):
    """契约事件"""

    # 事件类型
    type: str

    # 事件数据
    data: dict[str, Any] = {}


_queue: asyncio.Queue[RealtimeEvent] | None = None


def event_queue() -> asyncio.Queue[RealtimeEvent]:
    """有界事件队列 惰性单例"""
    global _queue
    if _queue is None:
        _queue = asyncio.Queue(maxsize=EVENT_QUEUE_MAX)
    return _queue


def publish(event: RealtimeEvent) -> bool:
    """发布事件 队满丢弃最旧 返回是否入队"""
    queue = event_queue()
    try:
        queue.put_nowait(event)
        return True
    except asyncio.QueueFull:
        queue.get_nowait()
        queue.put_nowait(event)
        return False
