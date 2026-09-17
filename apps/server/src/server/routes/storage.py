"""对象存储路由"""

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Annotated

from aiobotocore.client import AioBaseClient
from botocore.exceptions import ClientError
from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse

from server.adapters import storage
from server.adapters.storage import get_storage
from server.services import storage as storage_service

if TYPE_CHECKING:
    # 流式对象体 仅注解使用
    from aiobotocore.response import AioStreamingBody

# 路由 契约未定义本资源 不进接口规范
router = APIRouter(prefix="/storage", tags=["storage"], include_in_schema=False)


def _chunks(file: UploadFile) -> AsyncIterator[bytes]:
    """分块读取上传文件"""

    async def stream() -> AsyncIterator[bytes]:
        while chunk := await file.read(storage.CHUNK_SIZE):
            yield chunk

    return stream()


@router.post(
    path="/objects",
    description="上传对象",
    status_code=status.HTTP_200_OK,
)
async def upload_object(
    path: str,
    file: UploadFile,
    client: Annotated[AioBaseClient, Depends(get_storage)],
    x_tenant_id: Annotated[str, Header()] = storage.DEFAULT_TENANT,
) -> dict:
    """流式上传 超上限 413"""
    try:
        key = await storage_service.upload_object(
            client, x_tenant_id, path, _chunks(file)
        )
    except storage.PayloadTooLargeError:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="对象超过流式上传上限",
        ) from None
    return {"code": 0, "message": "ok", "data": {"key": key}}


@router.get(
    path="/objects/{key:path}",
    description="下载对象",
    status_code=status.HTTP_200_OK,
)
async def download_object(
    key: str,
    client: Annotated[AioBaseClient, Depends(get_storage)],
    x_tenant_id: Annotated[str, Header()] = storage.DEFAULT_TENANT,
) -> StreamingResponse:
    """流式下载 不存在 404"""
    try:
        body: AioStreamingBody = await storage_service.open_object(
            client, x_tenant_id, key
        )
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") != "NoSuchKey":
            raise
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="对象不存在"
        ) from None
    return StreamingResponse(storage.iter_chunks(body))
