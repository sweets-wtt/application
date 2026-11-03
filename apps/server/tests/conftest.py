"""测试共享 fixture"""

import os
from pathlib import Path

import pytest

# 工作流系统库隔离 - 必须早于 server.main 导入, 否则应用启动时会先读默认值
# 落仓库内 .test-data/, 与 data/ 同属运行时产物并已被忽略
_TEST_DB_DIR = Path(__file__).resolve().parents[3] / ".test-data"
_TEST_DB_DIR.mkdir(parents=True, exist_ok=True)
os.environ["APP_WORKFLOW__SYSTEM_DATABASE_URL"] = (
    "sqlite:///" + (_TEST_DB_DIR / "workflow.sqlite").as_posix()
)

from fastapi import FastAPI  # noqa: E402
from server.main import app as application  # noqa: E402


@pytest.fixture(scope="session")
def app() -> FastAPI:
    """应用实例"""
    return application
