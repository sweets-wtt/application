"""客户端测试"""

from contextlib import AbstractAsyncContextManager

from aiobotocore.client import AioBaseClient
from app.storage import create_client


async def test_create_client() -> None:
    """客户端为异步上下文管理器 进入后可用"""
    manager = create_client(
        endpoint_url="http://garage:3900",
        region_name="garage",
        aws_access_key_id="GKA000000000000000000",
        aws_secret_access_key="secret",
    )

    assert isinstance(manager, AbstractAsyncContextManager)

    async with manager as client:
        assert isinstance(client, AioBaseClient)
