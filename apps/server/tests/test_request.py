"""请求服务测试"""

from app.contracts.generated.http import WorkflowInput
from server.services import request as request_service


async def test_handle_uppercases_message() -> None:
    """处理请求 - 转大写"""
    result = await request_service.handle(WorkflowInput(message="hi"))

    assert result == "HI"
