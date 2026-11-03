"""Alembic 迁移环境"""

import asyncio
from logging.config import fileConfig

from alembic import context
from app.data import Base
from server.core import settings
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

# Alembic Config 对象
config = context.config

# 日志配置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 数据源名称 - 单一来源 settings
config.set_main_option("sqlalchemy.url", settings.database.url)

# 迁移目标元数据 - 由 ORM 模型提供, 供 autogenerate 比对
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """离线模式 - 仅生成 SQL"""
    url = config.get_main_option("sqlalchemy.url")

    # 离线上下文 - 参数字面绑定
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """在既有连接上执行迁移"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # 类型比对 - 避免方言差异导致的等价类型被误判
        compare_type=True,
        # 默认值比对 - 服务端默认值参与比较
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """在线模式 - 异步引擎执行迁移"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # 连接上执行迁移
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """在线模式入口"""
    asyncio.run(run_async_migrations())


# 离线生成 SQL、在线执行迁移
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
