"""测试共享 fixture"""

import pytest
from fastapi import FastAPI
from server.main import app as application


@pytest.fixture(scope="session")
def app() -> FastAPI:
    return application
