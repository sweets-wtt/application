"""路由聚合"""

from fastapi import APIRouter

from server.features.health.router import router as health_router


api_router = APIRouter()

# 注册业务路由
api_router.include_router(health_router)
