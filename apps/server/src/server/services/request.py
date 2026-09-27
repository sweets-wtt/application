"""请求服务"""

from app.contracts.generated.http import RequestInput


async def handle(input: RequestInput) -> str:
    """处理请求 - 转大写"""
    return input.message.upper()
