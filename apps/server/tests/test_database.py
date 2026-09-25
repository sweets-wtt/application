"""数据库适配器测试"""

from server.adapters.database import engine, get_session, session_factory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.pool import NullPool


def test_engine_pgbouncer_defaults() -> None:
    """引擎默认兼容 PgBouncer"""
    assert isinstance(engine.pool, NullPool)


def test_session_factory_reusable() -> None:
    """会话工厂可复用"""
    assert session_factory.kw["expire_on_commit"] is False


async def test_get_session_yields_session() -> None:
    """每请求会话产出 AsyncSession"""
    async for session in get_session():
        assert isinstance(session, AsyncSession)
