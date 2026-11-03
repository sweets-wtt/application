"""限流 - 应用层按客户端 IP 进程内计数"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from server.core import settings

limiter = Limiter(
    key_func=get_remote_address,
    # 存储不可用时不再拦截请求 - 限流降级优先于可用性
    swallow_errors=True,
    enabled=settings.rate_limit.enabled,
)

# 各端点限额 - 按成本区分
DEFAULT_LIMIT = settings.rate_limit.default_limit
