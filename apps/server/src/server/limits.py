"""限流 - 应用层按客户端 IP 计数

存储后端复用 Valkey 以支持多实例共享计数; 未配置存储地址时退回进程内计数。
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from server.core import settings


def _storage_uri() -> str | None:
    """限流存储地址 - 未配置时交由 SlowAPI 使用进程内存储"""
    return settings.rate_limit.storage_uri or None


limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=_storage_uri(),
    # 存储不可用时不再拦截请求 - 限流降级优先于可用性
    swallow_errors=True,
    enabled=settings.rate_limit.enabled,
)

# 各端点限额 - 按成本区分
DEFAULT_LIMIT = settings.rate_limit.default_limit
WORKFLOW_LIMIT = settings.rate_limit.workflow_limit
STORAGE_LIMIT = settings.rate_limit.storage_limit
