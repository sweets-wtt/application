"""存活探针路由"""

from app.log import get_logger
from fastapi import APIRouter

# 日志器
log = get_logger("healthz")

router = APIRouter(tags=["health"])


@router.get(path="/healthz", description="存活探针")
async def healthz() -> dict:
    """存活探针"""
    log.info("healthz")
    return {"code": 0, "message": "ok", "data": {"status": "ok"}}
