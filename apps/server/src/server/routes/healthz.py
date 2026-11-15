"""存活探针路由"""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get(path="/healthz", description="存活探针")
async def healthz() -> dict:
    """存活探针 - 返回 ok"""
    return {"code": 0, "message": "ok", "data": {"status": "ok"}}
