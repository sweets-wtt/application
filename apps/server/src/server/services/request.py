"""请求服务"""

from app.contracts.generated.http import WorkflowInput


async def handle(input: WorkflowInput) -> str:
    """处理请求 - 转大写"""
    return input.message.upper()
