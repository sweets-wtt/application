"""会话工厂测试"""

from app.db import create_engine, create_session_factory
from app.db.session import PGBOUNCER_CONNECT_ARGS, _connect_args
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker


def test_pgbouncer_connect_args() -> None:
    """PgBouncer 兼容参数禁用预备语句缓存"""
    assert PGBOUNCER_CONNECT_ARGS["prepared_statement_cache_size"] == 0


def test_connect_args_merge() -> None:
    """显式 connect_args 合并覆盖默认值"""
    assert _connect_args({}) == {"prepared_statement_cache_size": 0}
    assert _connect_args({"timeout": 10}) == {
        "prepared_statement_cache_size": 0,
        "timeout": 10,
    }
    assert _connect_args({"prepared_statement_cache_size": 10}) == {
        "prepared_statement_cache_size": 10,
    }


async def test_create_engine() -> None:
    """引擎可创建且可释放"""
    engine = create_engine("postgresql+asyncpg://app:app@localhost:5432/app")

    assert isinstance(engine, AsyncEngine)
    await engine.dispose()


async def test_create_engine_with_connect_args() -> None:
    """自定义 connect_args 引擎可创建且可释放"""
    engine = create_engine(
        "postgresql+asyncpg://app:app@localhost:5432/app",
        connect_args={"timeout": 10},
    )

    assert isinstance(engine, AsyncEngine)
    await engine.dispose()


async def test_create_session_factory() -> None:
    """会话工厂产生会话且提交后不过期"""
    engine = create_engine("postgresql+asyncpg://app:app@localhost:5432/app")
    factory = create_session_factory(engine)

    assert isinstance(factory, async_sessionmaker)

    async with factory() as session:
        assert isinstance(session, AsyncSession)
        assert session.sync_session.expire_on_commit is False

    await engine.dispose()
