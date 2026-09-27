"""契约模糊测试"""

import schemathesis
from server.adapters.database import get_session
from server.adapters.workflow import get_client
from server.main import app

# 契约单一来源 - 直接加载契约文件
schema = schemathesis.openapi.from_path("contracts/http/openapi.yaml")


# 离线桩 - 外部依赖(Hatchet/数据库)在测试环境不可用,模糊测试只验证契约符合性
class _FakeRun:
    """工作流 run 引用桩"""

    workflow_run_id = "run-test"


class _FakeWorkflow:
    """工作流桩"""

    async def aio_run_no_wait(self, _payload: object) -> _FakeRun:
        return _FakeRun()


class _FakeClient:
    """Hatchet 客户端桩"""

    def workflow(self, **_kwargs: object) -> _FakeWorkflow:
        return _FakeWorkflow()


class _FakeResult:
    """查询结果桩"""

    def first(self) -> None:
        return None


class _FakeSession:
    """数据库会话桩"""

    async def execute(self, _stmt: object, _params: object = None) -> _FakeResult:
        return _FakeResult()

    async def commit(self) -> None:
        pass


# 覆盖外部依赖
app.dependency_overrides[get_client] = lambda: _FakeClient()
app.dependency_overrides[get_session] = lambda: _FakeSession()


@schema.parametrize()
def test_api(case):
    case.call_and_validate(app=app)
