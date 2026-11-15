"""应用入口"""

import fastapi

from server.api.router import api_router
from server.core.bootstrap import bootstrap
from server.core.exceptions import AppError
from server.core.exceptions import handle_app_error


# 装配依赖 - 初始化日志等, 须先于应用实例化
bootstrap()

# 应用实例
app = fastapi.FastAPI(title="Server")

# 业务异常 - 统一错误结构
app.add_exception_handler(AppError, handle_app_error)

# 注册路由
app.include_router(api_router)
