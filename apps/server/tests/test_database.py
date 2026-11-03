"""数据库适配器测试"""

from server.adapters import engine, get_session, session_factory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.pool import NullPool


def test_engine_uses_default_pool() -> None:
    """引擎使用 SQLAlchemy 默认连接池 - 直连场景不强制空池"""
    assert not isinstance(engine.pool, NullPool)


def test_session_factory_reusable() -> None:
    """会话工厂可复用"""
    assert session_factory.kw["expire_on_commit"] is False


async def test_get_session_yields_session() -> None:
    """每请求会话产出 AsyncSession"""
    async for session in get_session():
        assert isinstance(session, AsyncSession)
