"""契约模型测试"""

import pydantic
from app.contracts.generated import http


def test_generated_models_are_pydantic() -> None:
    """生成的契约模型为 Pydantic 模型"""
    models = [
        member
        for member in (getattr(http, name) for name in dir(http))
        if isinstance(member, type) and issubclass(member, pydantic.BaseModel)
    ]

    assert models


def test_healthz_get_response() -> None:
    """存活探针响应模型可解析"""
    model = http.HealthzGetResponse.model_validate(
        {"code": 0, "message": "ok", "data": {"status": "ok"}}
    )

    assert model.code == 0
    assert model.data.status == "ok"
