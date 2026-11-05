"""路由聚合"""

from fastapi import APIRouter

from server.api.routes import utils


api_router = APIRouter()
api_router.include_router(utils.router)
