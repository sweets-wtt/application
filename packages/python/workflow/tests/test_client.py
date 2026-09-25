"""工作流客户端测试"""

import pytest
from app.workflow.client import WorkflowSettings, create_client


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """从环境变量装配参数"""
    monkeypatch.setenv("APP_WORKFLOW_TOKEN", "t")
    monkeypatch.setenv("APP_WORKFLOW_SERVER_URL", "http://hatchet:7070")

    settings = WorkflowSettings.from_env()

    assert settings == WorkflowSettings(token="t", server_url="http://hatchet:7070")


def test_create_client_injects_config() -> None:
    """创建客户端时注入装配参数"""

    class FakeHatchet:
        def __init__(self, **kwargs: object) -> None:
            self.kwargs = kwargs

    settings = WorkflowSettings(token="t", server_url="http://hatchet:7070")

    client = create_client(settings, client_factory=FakeHatchet)

    assert client.kwargs == {"token": "t", "server_url": "http://hatchet:7070"}
