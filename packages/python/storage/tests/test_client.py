"""对象存储客户端测试"""

import pytest
from app.storage.client import StorageSettings, create_client


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """从环境变量装配参数"""
    monkeypatch.setenv("APP_STORAGE_ENDPOINT", "http://garage:3900")
    monkeypatch.setenv("APP_STORAGE_ACCESS_KEY", "ak")
    monkeypatch.setenv("APP_STORAGE_SECRET_KEY", "sk")
    monkeypatch.setenv("APP_STORAGE_BUCKET", "app")

    settings = StorageSettings.from_env()

    assert settings == StorageSettings(
        endpoint_url="http://garage:3900",
        access_key_id="ak",
        secret_access_key="sk",
        region_name="garage",
        bucket="app",
    )


async def test_create_client_assembles_target() -> None:
    """客户端装配端点与区域。不产生网络请求"""
    settings = StorageSettings(
        endpoint_url="http://garage:3900",
        access_key_id="ak",
        secret_access_key="sk",
        region_name="garage",
        bucket="app",
    )

    async with create_client(settings) as client:
        assert client.meta.endpoint_url == "http://garage:3900"
        assert client.meta.region_name == "garage"
        assert client.meta.service_model.service_name == "s3"
