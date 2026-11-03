"""工作流集成测试 - 需可用的工作流系统库"""

import os

import pytest

# 缺少系统库连接串则跳过 - 离线安全
pytestmark = pytest.mark.skipif(
    not os.environ.get("APP_WORKFLOW__SYSTEM_DATABASE_URL"),
    reason="需工作流系统库",
)
