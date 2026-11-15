"""数据库会话测试"""

from app.db import create_engine, create_session_factory
from app.db.session import _engine_kwargs
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.pool import NullPool


def test_engine_kwargs_pgbouncer_defaults() -> None:
    """引擎参数默认兼容 PgBouncer"""
    kwargs = _engine_kwargs({})

    assert kwargs["poolclass"] is NullPool
    assert kwargs["connect_args"]["statement_cache_size"] == 0


def test_engine_kwargs_options_override() -> None:
    """显式参数覆盖默认值"""
    kwargs = _engine_kwargs({"poolclass": None, "connect_args": {"timeout": 5}})

    assert kwargs["poolclass"] is None
    assert kwargs["connect_args"] == {"timeout": 5, "statement_cache_size": 0}


def test_create_engine_pool() -> None:
    """引擎使用空连接池"""
    engine = create_engine("postgresql+asyncpg://")

    assert isinstance(engine.pool, NullPool)


def test_create_session_factory_yields_session() -> None:
    """会话工厂产出异步会话"""
    engine = create_engine("postgresql+asyncpg://")
    factory = create_session_factory(engine)

    assert isinstance(factory(), AsyncSession)
