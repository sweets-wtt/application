"""路由聚合"""

from fastapi import FastAPI

from server.routes.healthz import router as healthz_router


def include_routes(app: FastAPI) -> None:
    """注册全部路由"""
    app.include_router(healthz_router)
