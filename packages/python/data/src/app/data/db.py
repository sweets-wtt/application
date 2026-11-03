"""数据库会话工厂"""

from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_engine(url: str, **options: Any) -> AsyncEngine:
    """创建异步引擎

    直连数据库, 使用 SQLAlchemy 默认连接池与预编译语句缓存。
    """
    return create_async_engine(url, **options)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """创建会话工厂"""
    return async_sessionmaker(engine, expire_on_commit=False)
