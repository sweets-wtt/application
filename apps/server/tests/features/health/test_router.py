"""健康检查契约测试"""

from pathlib import Path

import schemathesis
from schemathesis import Case

from server.main import app


# 契约单一来源 - 直接加载仓库根下的契约文件
_SCHEMA_PATH = Path(__file__).resolve().parents[5] / "contracts/http/dist/openapi.yaml"

schema = schemathesis.openapi.from_path(_SCHEMA_PATH)


@schema.parametrize()
def test_api(case: Case) -> None:
    """按契约生成的用例逐个校验"""
    case.call_and_validate(app=app)
