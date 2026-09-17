"""实时路由"""

from typing import Annotated

from app.cache import CacheClient
from fastapi import APIRouter, Depends, Header, HTTPException, status

from server.adapters import realtime as realtime_adapter
from server.adapters.cache import get_cache
from server.core.settings import realtime_settings

# 路由 契约未定义本资源 不进接口规范
router = APIRouter(prefix="/realtime", tags=["realtime"], include_in_schema=False)


@router.post(
    path="/tickets",
    description="签发一次性实时票据",
    status_code=status.HTTP_200_OK,
)
async def create_ticket(
    cache: Annotated[CacheClient, Depends(get_cache)],
    origin: Annotated[str | None, Header()] = None,
) -> dict:
    """Origin 允许列表校验通过后签发一次性票据"""
    if origin is None or origin not in realtime_settings.realtime.origins:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Origin 不在允许列表"
        )
    ticket = realtime_adapter.new_ticket()
    if not await realtime_adapter.issue_ticket(cache, ticket):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="票据签发失败"
        )
    return {"code": 0, "message": "ok", "data": {"ticket": ticket}}
