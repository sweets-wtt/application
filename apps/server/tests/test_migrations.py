"""迁移测试"""

from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

# Server 目录
SERVER_ROOT = Path(__file__).resolve().parents[1]


def make_config() -> Config:
    """构造迁移配置 不读 ini URL 由 alembic/env.py 注入"""
    config = Config()
    config.set_main_option("script_location", str(SERVER_ROOT / "alembic"))
    return config


def test_script_directory() -> None:
    """迁移脚本目录可加载"""
    script = ScriptDirectory.from_config(make_config())

    assert list(script.walk_revisions()) == []


def test_upgrade_offline() -> None:
    """离线升级仅生成 SQL 不连库"""
    command.upgrade(make_config(), "head", sql=True)
