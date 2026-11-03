"""数据库会话测试"""

from typing import Any

import pytest
from app.data.db import create_engine, create_session_factory
from sqlalchemy.ext.asyncio import AsyncSession


def _capture_kwargs(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """拦截引擎构造以捕获传入参数"""
    captured: dict[str, Any] = {}

    def fake_create(_url: str, **kwargs: Any) -> object:
        captured.update(kwargs)
        return object()

    monkeypatch.setattr("app.data.db.create_async_engine", fake_create)
    return captured


def test_create_engine_pool_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """未显式指定时使用设计默认值"""
    captured = _capture_kwargs(monkeypatch)

    create_engine("postgresql+asyncpg://")

    assert captured["pool_size"] == 5
    assert captured["max_overflow"] == 10
    assert captured["pool_timeout"] == 30
    assert captured["pool_pre_ping"] is True
    assert captured["pool_recycle"] == 3600


def test_create_engine_pool_params_passthrough(monkeypatch: pytest.MonkeyPatch) -> None:
    """显式连接池参数覆盖默认值"""
    captured = _capture_kwargs(monkeypatch)

    create_engine(
        "postgresql+asyncpg://",
        pool_size=7,
        max_overflow=3,
        pool_timeout=12,
        pool_pre_ping=False,
        pool_recycle=600,
    )

    assert captured["pool_size"] == 7
    assert captured["max_overflow"] == 3
    assert captured["pool_timeout"] == 12
    assert captured["pool_pre_ping"] is False
    assert captured["pool_recycle"] == 600


def test_create_engine_sqlite_strips_pool_params(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SQLite 的池实现不接受这些参数, 需剥离"""
    captured = _capture_kwargs(monkeypatch)

    create_engine("sqlite:///x.db")

    assert "pool_size" not in captured
    assert "max_overflow" not in captured
    assert "pool_pre_ping" not in captured


def test_create_engine_uses_queue_pool() -> None:
    """真实引擎使用队列池而非空池"""
    engine = create_engine("postgresql+asyncpg://")

    assert engine.pool.__class__.__name__ == "AsyncAdaptedQueuePool"


def test_create_session_factory_yields_session() -> None:
    """会话工厂产出异步会话"""
    engine = create_engine("postgresql+asyncpg://")
    factory = create_session_factory(engine)

    assert isinstance(factory(), AsyncSession)
