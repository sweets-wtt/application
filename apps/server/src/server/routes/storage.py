"""对象存储路由"""

from typing import Annotated

from aiobotocore.client import AioBaseClient
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from starlette.responses import StreamingResponse

from server.adapters.storage import get_client
from server.services import storage as storage_service

router = APIRouter(prefix="/storage", tags=["storage"])


@router.put("/{key:path}", description="流式上传对象")
async def put_object(
    request: Request,
    key: str,
    x_tenant: Annotated[str, Header(description="租户标识")],
    client: Annotated[AioBaseClient, Depends(get_client)],
) -> dict:
    """流式上传对象 - 超限返回 413"""
    # 流式读取请求体并计数
    try:
        size = await storage_service.upload(client, x_tenant, key, request.stream())
    except storage_service.UploadTooLarge:
        raise HTTPException(status_code=413, detail="上传超过 10 MiB") from None

    return {"code": 0, "message": "ok", "data": {"key": key, "size": size}}


@router.get("/{key:path}", description="流式下载对象")
async def get_object(
    key: str,
    x_tenant: Annotated[str, Header(description="租户标识")],
    client: Annotated[AioBaseClient, Depends(get_client)],
) -> Response:
    """流式下载对象 - 不存在返回 404"""
    try:
        stream = await storage_service.download(client, x_tenant, key)
    except storage_service.NotFound:
        raise HTTPException(status_code=404, detail="对象不存在") from None

    return StreamingResponse(stream, media_type="application/octet-stream")
