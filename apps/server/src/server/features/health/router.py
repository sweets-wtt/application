"""健康检查路由"""

from fastapi import APIRouter


# 健康检查路由
router = APIRouter(tags=["health"])


@router.get(path="/healthz", description="存活探针")
async def get_health() -> dict:
    """存活探针 - 返回 ok"""
    return {"code": 0, "message": "ok", "data": {"status": "ok"}}
