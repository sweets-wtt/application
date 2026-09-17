"""测试共享 fixture"""

import os

import pytest
from fastapi import FastAPI


def pytest_configure(config: pytest.Config) -> None:
    """测试环境配置 engine 与客户端构造为惰性 不建立连接"""
    os.environ.setdefault(
        "DATABASE__URL", "postgresql+asyncpg://app:app@localhost:5432/app"
    )
    os.environ.setdefault("STORAGE__URL", "http://garage:3900")
    os.environ.setdefault("STORAGE__REGION", "garage")
    os.environ.setdefault("STORAGE__ACCESS_KEY_ID", "GKA000000000000000000")
    os.environ.setdefault("STORAGE__SECRET_ACCESS_KEY", "secret")
    os.environ.setdefault("STORAGE__BUCKET", "app")
    os.environ.setdefault("CACHE__URL", "valkey://localhost:6379/0")
    os.environ.setdefault("REALTIME__ORIGINS", '["https://app.example.com"]')


@pytest.fixture(scope="session")
def app() -> FastAPI:
    from server.main import app as application

    return application
