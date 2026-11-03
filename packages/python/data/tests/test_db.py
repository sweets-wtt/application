"""数据库会话测试"""

from app.data.db import create_engine, create_session_factory
from sqlalchemy.ext.asyncio import AsyncSession


def test_create_engine_uses_default_pool() -> None:
    """引擎使用 SQLAlchemy 默认连接池"""
    engine = create_engine("postgresql+asyncpg://")

    # 直连场景不再强制空连接池
    assert engine.pool.__class__.__name__ != "NullPool"


def test_create_engine_options_passthrough() -> None:
    """显式参数原样透传给引擎"""
    engine = create_engine("postgresql+asyncpg://", echo=False)

    assert engine.echo is False


def test_create_session_factory_yields_session() -> None:
    """会话工厂产出异步会话"""
    engine = create_engine("postgresql+asyncpg://")
    factory = create_session_factory(engine)

    assert isinstance(factory(), AsyncSession)
