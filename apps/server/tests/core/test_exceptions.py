"""业务异常测试"""

import json

from fastapi import Request
from fastapi.responses import JSONResponse
import pytest

from server.core.exceptions import AppError
from server.core.exceptions import handle_app_error


# 找不到资源状态码
NOT_FOUND = 404
# 内部错误状态码
INTERNAL_ERROR = 500


class NotFoundError(AppError):
    """找不到资源"""

    status_code = NOT_FOUND
    detail = "资源不存在"


@pytest.fixture
def request_stub() -> Request:
    """请求占位 - 处理器未使用该参数"""
    return Request({"type": "http", "headers": [], "query_string": b""})


def payload(response: JSONResponse) -> object:
    """响应体解析"""
    body = response.body
    raw = bytes(body) if isinstance(body, memoryview) else body

    return json.loads(raw)


async def test_app_error_default_detail(request_stub: Request) -> None:
    """默认描述 - 使用类属性"""
    response = await handle_app_error(request_stub, NotFoundError())

    assert response.status_code == NOT_FOUND
    assert payload(response) == {"detail": "资源不存在"}


async def test_app_error_custom_detail(request_stub: Request) -> None:
    """自定义描述 - 覆盖类属性"""
    response = await handle_app_error(request_stub, NotFoundError("画布不存在"))

    assert response.status_code == NOT_FOUND
    assert payload(response) == {"detail": "画布不存在"}


async def test_app_error_base_defaults(request_stub: Request) -> None:
    """基类默认值 - 500 与内部错误"""
    response = await handle_app_error(request_stub, AppError())

    assert response.status_code == INTERNAL_ERROR
    assert payload(response) == {"detail": "内部错误"}


async def test_non_app_error_falls_back(request_stub: Request) -> None:
    """非业务异常 - 回退为内部错误"""
    response = await handle_app_error(request_stub, ValueError("boom"))

    assert response.status_code == INTERNAL_ERROR
    assert payload(response) == {"detail": "内部错误"}
