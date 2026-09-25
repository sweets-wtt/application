"""数据库适配器"""

from collections.abc import AsyncIterator

from app.db import create_engine, create_session_factory
from sqlalchemy.ext.asyncio import AsyncSession

from server.core.settings import settings

# 异步引擎 - PgBouncer 兼容默认值由 app.db 提供
engine = create_engine(settings.database.url)

# 会话工厂 - api 每请求 / worker 任务共用
session_factory = create_session_factory(engine)


async def get_session() -> AsyncIterator[AsyncSession]:
    """api 服务每请求会话"""
    async with session_factory() as session:
        yield session
