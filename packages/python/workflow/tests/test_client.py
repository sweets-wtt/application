"""工作流客户端测试"""

import pytest
from app.workflow.client import WorkflowClient, WorkflowSettings, create_client


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """从环境变量装配参数"""
    monkeypatch.setenv("APP_WORKFLOW_SYSTEM_DATABASE_URL", "sqlite:///app.sqlite")

    settings = WorkflowSettings.from_env()

    assert settings == WorkflowSettings(system_database_url="sqlite:///app.sqlite")


def test_create_client_returns_client() -> None:
    """创建客户端返回装配好的实例"""
    settings = WorkflowSettings(system_database_url="sqlite:///app.sqlite")

    client = create_client(settings)

    assert isinstance(client, WorkflowClient)


def test_sqlite_parent_dir_created(tmp_path) -> None:
    """SQLite 系统库的父目录缺失时自动创建"""
    db_path = tmp_path / "nested" / "deeper" / "workflow.sqlite"
    settings = WorkflowSettings(system_database_url=f"sqlite:///{db_path.as_posix()}")

    client = create_client(settings)
    client._ensure_sqlite_dir()

    assert db_path.parent.is_dir()
