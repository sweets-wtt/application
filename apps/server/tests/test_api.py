"""契约模糊测试"""

from types import SimpleNamespace

import schemathesis
from server.adapters import get_workflow_client as get_client
from server.main import app

# 契约单一来源 - 直接加载契约文件
schema = schemathesis.openapi.from_path("contracts/http/dist/openapi.yaml")


# 离线桩 - 外部依赖(工作流)在测试环境不可用,
# 模糊测试只验证契约符合性
class _FakeClient:
    """工作流客户端桩 - 固定 run_id 与 SUCCESS 状态"""

    def start(self, _workflow: object, _payload: object, _workflow_id: str) -> str:
        return "run-test"

    def status(self, _run_id: str) -> SimpleNamespace:
        return SimpleNamespace(status="SUCCESS")


# 覆盖外部依赖
app.dependency_overrides[get_client] = lambda: _FakeClient()


@schema.parametrize()
def test_api(case):
    # 认证端点涉及浏览器跳转与 Cookie, 由 test_auth 覆盖
    if case.operation.path.startswith("/auth/"):
        return

    case.call_and_validate(app=app)
