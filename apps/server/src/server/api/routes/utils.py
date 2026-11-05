"""工具路由"""

from fastapi import APIRouter


router = APIRouter(tags=["utils"])


@router.get(path="/healthz", description="存活探针")
async def health_check() -> dict:
    """存活探针 - 返回 ok"""
    return {"code": 0, "message": "ok", "data": {"status": "ok"}}
