"""契约模糊测试"""

import schemathesis
from server.main import app

# 契约单一来源 - 直接加载契约文件
schema = schemathesis.openapi.from_path("contracts/http/dist/openapi.yaml")


@schema.parametrize()
def test_api(case):
    # 认证端点涉及浏览器跳转与 Cookie, 由 test_auth 覆盖
    if case.operation.path.startswith("/auth/"):
        return

    case.call_and_validate(app=app)
