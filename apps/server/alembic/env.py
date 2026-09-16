"""Alembic 迁移环境"""

import asyncio
from logging.config import fileConfig

from alembic import context
from server.core.settings import db_settings
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Alembic Config 对象 提供对 ini 配置值的访问
config = context.config

# 解析配置文件的 Python 日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 模型元数据 供 autogenerate 支持
target_metadata = None

# 注入连接 URL 经 set_main_option 覆盖 ini 值
config.set_main_option("sqlalchemy.url", db_settings.database.url)


def run_migrations_offline() -> None:
    """离线迁移 仅生成 SQL 不连库"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """在线迁移回调"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """经异步引擎迁移 官方 NullPool + run_sync"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """在线迁移"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
