"""数据库会话工厂"""

from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_engine(
    url: str,
    *,
    pool_size: int = 5,
    max_overflow: int = 10,
    pool_timeout: int = 30,
    pool_pre_ping: bool = True,
    pool_recycle: int = 3600,
    **options: Any,
) -> AsyncEngine:
    """创建异步引擎

    显式声明连接池参数, 由池自行探活与到期重建,
    避免容器重启或中间设备静默断连后取到死连接。
    SQLite 的池实现不接受这些参数, 需剥离。
    """
    if url.startswith("sqlite"):
        return create_async_engine(url, **options)

    return create_async_engine(
        url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_pre_ping=pool_pre_ping,
        pool_recycle=pool_recycle,
        **options,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """创建会话工厂"""
    return async_sessionmaker(engine, expire_on_commit=False)
