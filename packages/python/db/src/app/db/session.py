"""数据库会话工厂 - https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

会话经 async with 使用并自动关闭
单 session 不跨并发任务共享
engine 出作用域前 await dispose()
"""

from collections.abc import Mapping
from typing import Any, Final

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# 禁用预备语句缓存以兼容 PgBouncer 事务池
# https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#prepared-statement-cache-with-asyncpg
PGBOUNCER_CONNECT_ARGS: Final[Mapping[str, Any]] = {"prepared_statement_cache_size": 0}


def _connect_args(overrides: Mapping[str, Any]) -> dict[str, Any]:
    """合并 PgBouncer 默认值 显式值优先"""
    return {**PGBOUNCER_CONNECT_ARGS, **overrides}


def create_engine(url: str, **kwargs: Any) -> AsyncEngine:
    """创建 PgBouncer 兼容的异步引擎"""
    overrides: Mapping[str, Any] = kwargs.pop("connect_args", {})
    return create_async_engine(url, connect_args=_connect_args(overrides), **kwargs)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """创建会话工厂

    expire_on_commit=False 避免 commit 后访问属性触发隐式 IO
    """
    return async_sessionmaker(engine, expire_on_commit=False)
