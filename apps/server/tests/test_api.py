"""契约模糊测试"""

import schemathesis
from server.main import app

# 契约单一来源 - 直接加载契约文件
schema = schemathesis.openapi.from_path("contracts/http/openapi.yaml")


@schema.parametrize()
def test_api(case):
    case.call_and_validate(app=app)
