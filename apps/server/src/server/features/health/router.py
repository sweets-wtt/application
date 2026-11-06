"""健康检查路由"""

from fastapi import APIRouter

from server.generated.contracts import Data
from server.generated.contracts import HealthzGetResponse


# 健康检查路由
router = APIRouter(tags=["health"])


@router.get(path="/healthz", description="存活探针")
async def get_health() -> HealthzGetResponse:
    """存活探针 - 返回 ok

    Returns:
        HealthzGetResponse: 统一信封的存活状态。
    """
    return HealthzGetResponse(code=0, message="ok", data=Data(status="ok"))
