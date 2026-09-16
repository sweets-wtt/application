"""数据库适配器测试"""

from server.adapters.database import engine, get_session, session_factory
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


async def test_get_session() -> None:
    """每请求会话 退出自动关闭"""
    generator = get_session()
    session = await anext(generator)

    assert isinstance(session, AsyncSession)

    await generator.aclose()


async def test_session_factory() -> None:
    """会话工厂可产生会话"""
    assert isinstance(engine, AsyncEngine)

    async with session_factory() as session:
        assert isinstance(session, AsyncSession)
