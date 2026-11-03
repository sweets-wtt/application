"""依赖装配测试"""

import pytest
from server import core


def test_setup_instruments_with_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """存在 OpenObserve 令牌才接线遥测"""
    calls: list[bool] = []
    monkeypatch.setattr(core, "configure", lambda: None)
    monkeypatch.setattr(core, "_instrument", lambda: calls.append(True))
    monkeypatch.setenv("APP_LOG_LEVEL", "INFO")
    monkeypatch.setenv("APP_LOG_FORMAT", "console")
    monkeypatch.setenv("OPENOBSERVE_AUTH_TOKEN", "Basic dGVzdDp0ZXN0")

    core.setup()

    assert calls == [True]


def test_setup_skips_instrumentation_without_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """缺省 OpenObserve 令牌不接线 - 测试离线安全"""
    calls: list[bool] = []
    monkeypatch.setattr(core, "configure", lambda: None)
    monkeypatch.setattr(core, "_instrument", lambda: calls.append(True))
    monkeypatch.setenv("APP_LOG_LEVEL", "INFO")
    monkeypatch.setenv("APP_LOG_FORMAT", "console")
    monkeypatch.delenv("OPENOBSERVE_AUTH_TOKEN", raising=False)

    core.setup()

    assert calls == []
