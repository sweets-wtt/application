"""迁移测试"""

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


def test_migrations_script_loadable() -> None:
    """迁移脚本目录可加载"""
    config = Config("apps/server/alembic.ini")
    script = ScriptDirectory.from_config(config)

    assert list(script.walk_revisions()) == []


def test_env_py_syntax() -> None:
    """迁移环境脚本语法有效"""
    source = Path("apps/server/alembic/env.py").read_text(encoding="utf-8")

    compile(source, "env.py", "exec")
