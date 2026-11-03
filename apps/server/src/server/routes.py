"""HTTP 路由 - 全部端点"""

import fastapi
from fastapi import APIRouter, Request

from server.limits import DEFAULT_LIMIT, limiter

# 存活探针
healthz_router = APIRouter(tags=["health"])


@healthz_router.get(path="/healthz", description="存活探针")
@limiter.limit(DEFAULT_LIMIT)
async def get_healthz(request: Request) -> dict:
    """存活探针 - 返回 ok"""
    return {"code": 0, "message": "ok", "data": {"status": "ok"}}


def include_routes(app: fastapi.FastAPI) -> None:
    """注册全部路由"""
    app.include_router(healthz_router)
