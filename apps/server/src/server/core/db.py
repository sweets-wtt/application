"""数据库引擎与会话"""

from collections.abc import AsyncIterator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase

from server.core.config import settings


# 约束命名约定 - 供 Alembic autogenerate 稳定识别约束
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """模型基类 - 承载全部表元数据, 供 Alembic autogenerate 使用"""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def create_engine() -> AsyncEngine:
    """创建异步引擎"""
    return create_async_engine(
        settings.database.url,
        echo=settings.database.echo,
    )


# 进程级引擎与会话工厂
engine = create_engine()
session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """每请求生命周期的数据库会话"""
    async with session_factory() as session:
        yield session
