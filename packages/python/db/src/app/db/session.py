"""数据库会话工厂"""

from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool


def _engine_kwargs(options: dict[str, Any]) -> dict[str, Any]:
    """填充 PgBouncer 兼容的默认参数

    事务池模式下连接池与预编译语句缓存交由 PgBouncer 管理
    """
    kwargs = dict(options)
    kwargs.setdefault("poolclass", NullPool)
    connect_args: dict[str, Any] = kwargs.setdefault("connect_args", {})
    connect_args.setdefault("statement_cache_size", 0)
    return kwargs


def create_engine(url: str, **options: Any) -> AsyncEngine:
    """创建 PgBouncer 兼容的异步引擎"""
    return create_async_engine(url, **_engine_kwargs(options))


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """创建会话工厂"""
    return async_sessionmaker(engine, expire_on_commit=False)
