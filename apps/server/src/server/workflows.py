"""工作流定义 - DBOS 持久执行

workflow 与 step 在 DBOS.launch 之前定义, 装饰器即完成注册。
"""

from app.contracts.generated.http import WorkflowInput
from dbos import DBOS

from server.core import WORKFLOW_NAME


@DBOS.step()
async def handle(input: WorkflowInput) -> str:
    """处理请求 - 转大写"""
    return input.message.upper()


@DBOS.workflow(name=WORKFLOW_NAME)
async def process(input: WorkflowInput) -> str:
    """工作流 - 处理请求"""
    return await handle(input)
