"""认证与权限测试"""

import asyncio
from typing import Any

import pytest
from fastapi import HTTPException
from server import auth
from starlette.requests import Request


def test_principal_maps_tenant_roles_and_scope() -> None:
    """令牌声明映射为租户、角色与权限"""
    principal = auth._principal_from_claims(
        {
            "sub": "user-1",
            "owner": "tenant-a",
            "roles": ["application/editor"],
            "email": "user@example.com",
            "name": "User",
            "scope": "custom:perm",
        }
    )

    assert principal.user_id == "user-1"
    assert principal.tenant_id == "tenant-a"
    assert principal.roles == ("editor",)
    assert "workflow:write" in principal.permissions
    assert "custom:perm" in principal.permissions
    assert "telemetry:write" in principal.permissions
    assert principal.email == "user@example.com"


def test_principal_admin_gets_all_permissions() -> None:
    """Casdoor 管理员声明映射为全权限"""
    principal = auth._principal_from_claims(
        {"sub": "admin-1", "isAdmin": True, "owner": "tenant-a"}
    )

    assert principal.roles == ("admin",)
    assert principal.permissions == frozenset({"*"})


def test_require_permission_denies_missing_permission() -> None:
    """缺少权限时返回 403"""
    dependency = auth.require_permission("workflow:write")
    principal = auth.Principal(
        user_id="user-1",
        tenant_id="tenant-a",
        email=None,
        name=None,
        roles=("viewer",),
        permissions=frozenset({"telemetry:write"}),
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(dependency(principal))

    assert exc.value.status_code == 403


def test_login_builds_casdoor_redirect(monkeypatch: pytest.MonkeyPatch) -> None:
    """登录生成 Casdoor 授权跳转与 state Cookie"""
    monkeypatch.setattr(auth.settings.auth, "enabled", True)
    monkeypatch.setattr(auth.settings.auth, "client_id", "app-web")
    monkeypatch.setattr(auth.settings.auth, "client_secret", "secret")
    monkeypatch.setattr(auth.settings.auth, "state_secret", "state-secret")
    monkeypatch.setattr(auth.settings.auth, "public_url", "https://auth.localtest.me")
    monkeypatch.setattr(
        auth.settings.auth,
        "redirect_uri",
        "https://web.localtest.me/auth/callback",
    )

    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/auth/login",
            "query_string": b"next=/home",
            "headers": [],
        }
    )

    response = asyncio.run(auth.login(request))

    assert response.status_code == 302
    assert response.headers["location"].startswith(
        "https://auth.localtest.me/login/oauth/authorize?"
    )
    assert auth.STATE_COOKIE in response.headers["set-cookie"]


def test_get_principal_reads_bearer_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """启用认证后从 Bearer 读取并解析令牌"""
    monkeypatch.setattr(auth.settings.auth, "enabled", True)
    monkeypatch.setattr(
        auth,
        "_decode_token",
        lambda _token: {"sub": "user-1", "roles": ["viewer"], "owner": "tenant-a"},
    )

    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/auth/me",
            "headers": [(b"authorization", b"Bearer test-token")],
        }
    )

    principal: Any = asyncio.run(auth.get_principal(request))

    assert principal.user_id == "user-1"
    assert principal.tenant_id == "tenant-a"


def test_get_principal_returns_dev_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """认证关闭时返回本地主体"""
    monkeypatch.setattr(auth.settings.auth, "enabled", False)

    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/auth/me",
            "headers": [],
        }
    )

    principal = asyncio.run(auth.get_principal(request))

    assert principal.user_id == "local"
    assert principal.permissions == frozenset({"*"})
