"""契约模糊测试"""

import schemathesis
from server.main import app

schema = schemathesis.openapi.from_asgi("/openapi.json", app)


@schema.parametrize()
def test_api(case):
    case.call_and_validate()
