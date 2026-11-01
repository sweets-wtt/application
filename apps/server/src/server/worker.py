"""Worker 入口 - Hatchet 任务与工作流定义"""

from app.contracts.generated.http import WorkflowInput
from hatchet_sdk import Context

from server.adapters import get_workflow_client
from server.core import WORKFLOW_NAME, setup
from server.services import handle

# Hatchet 客户端
hatchet = get_workflow_client()

# 工作流声明 - 与提交侧一致
workflow = hatchet.workflow(name=WORKFLOW_NAME, input_validator=WorkflowInput)


@workflow.task()
async def process(input: WorkflowInput, ctx: Context) -> dict:
    """处理请求任务"""
    return {"processed": await handle(input)}


@hatchet.task(name="request:echo", input_validator=WorkflowInput)
async def echo(input: WorkflowInput, ctx: Context) -> dict:
    """独立任务 - 回显请求"""
    return {"message": input.message}


def main() -> None:
    """启动 worker

    worker.start() 阻塞且禁止在已有 asyncio 循环内执行,
    因此与 api 服务分进程。
    """
    # 装配日志与遥测
    setup()

    # 创建并启动 worker
    worker = get_workflow_client().worker(name="server-worker", workflows=[workflow])
    worker.start()


if __name__ == "__main__":
    main()
