import os

from server.core.config import settings
from server.core.logging import configure


def setup() -> None:
    """装配应用依赖"""

    # 日志环境变量默认值
    os.environ.setdefault("APP_LOG_LEVEL", settings.log_level)
    os.environ.setdefault("APP_LOG_FORMAT", settings.log_format)

    # 初始化日志
    configure()
