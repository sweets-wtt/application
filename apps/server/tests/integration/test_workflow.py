"""工作流集成测试 - 需 Hatchet 控制面"""

import os

import pytest

# 缺少令牌则跳过 - 离线安全
pytestmark = pytest.mark.skipif(
    not os.environ.get("HATCHET_CLIENT_TOKEN"),
    reason="需 Hatchet 控制面",
)
