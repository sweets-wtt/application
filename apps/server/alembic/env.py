"""Alembic 迁移环境配置"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from server import models  # noqa: F401
from server.core.config import settings
from server.core.db import Base


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 连接串单一来源 - 覆盖 ini 中的占位值
config.set_main_option("sqlalchemy.url", settings.database.url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """离线模式 - 仅生成 SQL 而不连库"""
    context.configure(
        url=settings.database.url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # SQLite 不支持多数 ALTER TABLE, 以重建表模拟
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_sync_migrations(connection: Connection) -> None:
    """同步执行迁移 - 由异步引擎回调"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # SQLite 不支持多数 ALTER TABLE, 以重建表模拟
        render_as_batch=True,
        # 字段类型与默认值一并比较
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """异步模式 - 创建异步引擎并执行迁移"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(run_sync_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """在线模式 - 连接真实数据库"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
