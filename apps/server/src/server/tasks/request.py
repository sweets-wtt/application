"""请求独立任务"""

from app.contracts.generated.http import RequestInput
from hatchet_sdk import Context

from server.adapters.workflow import get_client

# Hatchet 客户端
hatchet = get_client()


@hatchet.task(name="request:echo", input_validator=RequestInput)
async def echo(input: RequestInput, ctx: Context) -> dict:
    """独立任务 - 回显请求"""
    return {"message": input.message}
