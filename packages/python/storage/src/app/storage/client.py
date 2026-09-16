"""对象存储客户端"""

from contextlib import AbstractAsyncContextManager

from aiobotocore.client import AioBaseClient
from aiobotocore.session import get_session


def create_client(
    endpoint_url: str,
    region_name: str,
    aws_access_key_id: str,
    aws_secret_access_key: str,
) -> AbstractAsyncContextManager[AioBaseClient]:
    """创建 S3 客户端

    客户端为异步上下文管理器 进入后可用 退出自动关闭
    """
    session = get_session()
    return session.create_client(
        "s3",
        endpoint_url=endpoint_url,
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
