"""Worker 入口"""

# 导入触发工作流与任务注册 - 模块路径导入避免名称冲突
import server.tasks.request
import server.workflows.request  # noqa: F401
from server.adapters.workflow import build_worker
from server.core import dependencies


def main() -> None:
    """启动 worker

    worker.start() 阻塞且禁止在已有 asyncio 循环内调用,
    与 api 服务分进程
    """
    # 装配日志与遥测
    dependencies.setup()

    # 创建并启动 worker
    worker = build_worker()
    worker.start()


if __name__ == "__main__":
    main()
