"""请求服务测试"""

from app.contracts.generated.http import WorkflowInput
from server.workflows import handle


async def test_handle_uppercases_message() -> None:
    """处理请求 - 转大写"""
    result = await handle(WorkflowInput(message="hi"))

    assert result == "HI"
