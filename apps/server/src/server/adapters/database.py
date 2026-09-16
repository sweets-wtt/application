"""数据库适配器"""

from collections.abc import AsyncGenerator

from app.db import create_engine, create_session_factory
from sqlalchemy.ext.asyncio import AsyncSession

from server.core.settings import db_settings

# 引擎 进程内单例 惰性连接
engine = create_engine(db_settings.database.url)

# 会话工厂 api 每请求经 get_session worker Task 直接使用
session_factory = create_session_factory(engine)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """每请求会话 退出自动关闭"""
    async with session_factory() as session:
        yield session
