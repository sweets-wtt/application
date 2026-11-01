"""请求工作流"""

from app.contracts.generated.http import WorkflowInput
from hatchet_sdk import Context

from server.adapters.workflow import get_client
from server.services import request as request_service

# 工作流名 - 与提交侧一致
WORKFLOW_NAME = "request"

# Hatchet 客户端与工作流声明
hatchet = get_client()
workflow = hatchet.workflow(name=WORKFLOW_NAME, input_validator=WorkflowInput)


@workflow.task()
async def process(input: WorkflowInput, ctx: Context) -> dict:
    """处理请求任务"""
    result = await request_service.handle(input)

    return {"processed": result}
