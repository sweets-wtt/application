"""认证 - Casdoor OIDC 授权码与 JWT 校验"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import logging
import secrets
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated, Any
from urllib.parse import urlencode

import httpx
import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from itsdangerous import URLSafeTimedSerializer
from jwt import PyJWKClient

from server.core import settings

if TYPE_CHECKING:
    from jwt.types import Options

# 日志器
logger = logging.getLogger(__name__)

# 状态 Cookie
STATE_COOKIE = "app_auth_state"

# 会话 Cookie
SESSION_COOKIE = "app_session"

# 状态有效期
STATE_TTL_SECONDS = 600

# 角色对应权限 - 业务路由按权限校验
ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "admin": frozenset({"*"}),
    "editor": frozenset(
        {
            "workflow:read",
            "workflow:write",
            "telemetry:write",
        }
    ),
    "viewer": frozenset(
        {
            "workflow:read",
            "telemetry:write",
        }
    ),
    "user": frozenset(
        {
            "workflow:read",
            "workflow:write",
            "telemetry:write",
        }
    ),
}


@dataclass(frozen=True)
class Principal:
    """已认证主体"""

    # 用户标识
    user_id: str

    # 租户标识
    tenant_id: str

    # 邮箱
    email: str | None

    # 显示名
    name: str | None

    # 角色
    roles: tuple[str, ...]

    # 权限
    permissions: frozenset[str]


# 开发态主体
DEV_PRINCIPAL = Principal(
    user_id="local",
    tenant_id="default",
    email=None,
    name="本地开发",
    roles=("admin",),
    permissions=frozenset({"*"}),
)

# JWKS 客户端缓存
_jwks_clients: dict[str, PyJWKClient] = {}


def _urls() -> tuple[str, str, str, str]:
    """认证端点 - 浏览器用公网, 服务端用内网"""
    auth = settings.auth
    public = auth.public_url or auth.issuer
    internal = auth.internal_url or public

    authorize = auth.authorize_url or f"{public}/login/oauth/authorize"
    token = auth.token_url or f"{internal}/api/login/oauth/access_token"
    jwks = auth.jwks_url or f"{internal}/.well-known/jwks"
    logout = auth.logout_url or f"{public}/api/logout"

    return authorize, token, jwks, logout


def _serializer() -> URLSafeTimedSerializer:
    """状态签名器"""
    secret = settings.auth.state_secret or settings.auth.client_secret

    if not secret:
        raise RuntimeError("认证状态密钥未配置")

    return URLSafeTimedSerializer(secret)


def _jwks_client() -> PyJWKClient:
    """JWKS 客户端 - 按地址缓存"""
    _, _, jwks_url, _ = _urls()

    if not jwks_url:
        raise RuntimeError("JWKS 地址未配置")

    client = _jwks_clients.get(jwks_url)
    if client is None:
        client = PyJWKClient(jwks_url)
        _jwks_clients[jwks_url] = client

    return client


def _decode_token(token: str) -> dict[str, Any]:
    """校验 JWT - 签名、签发方、受众与时间"""
    key = _jwks_client().get_signing_key_from_jwt(token)

    required = ["exp", "iat", "sub"]
    kwargs: dict[str, Any] = {}

    if settings.auth.issuer:
        required.append("iss")
        kwargs["issuer"] = settings.auth.issuer

    if settings.auth.client_id:
        required.append("aud")
        kwargs["audience"] = settings.auth.client_id

    options: Options = {"require": required}

    return jwt.decode(
        token,
        key.key,
        algorithms=["RS256", "RS512", "ES256", "ES384", "ES512"],
        options=options,
        **kwargs,
    )


def _principal_from_claims(claims: dict[str, Any]) -> Principal:
    """令牌声明 -> 主体"""
    user_id = claims.get("sub")
    if not isinstance(user_id, str) or not user_id:
        raise ValueError("令牌缺少 sub")

    raw_roles = claims.get(settings.auth.role_claim)
    if isinstance(raw_roles, str):
        roles = [raw_roles]
    elif isinstance(raw_roles, list):
        roles = [str(role) for role in raw_roles]
    else:
        roles = []

    # Casdoor 可能返回 org/role, 业务侧只使用角色名
    roles = [role.rsplit("/", 1)[-1] for role in roles]

    if claims.get("isAdmin") is True:
        roles.append("admin")

    if not roles:
        roles = ["user"]

    roles = list(dict.fromkeys(roles))

    permissions: set[str] = set()
    for role in roles:
        permissions.update(ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["user"]))

    scope = claims.get("scope")
    if isinstance(scope, str):
        permissions.update(scope.split())

    tenant = claims.get(settings.auth.tenant_claim)
    tenant_id = str(tenant) if tenant else "default"

    email = claims.get("email")
    name = claims.get("name") or claims.get("displayName")

    return Principal(
        user_id=user_id,
        tenant_id=tenant_id,
        email=str(email) if email else None,
        name=str(name) if name else None,
        roles=tuple(roles),
        permissions=frozenset(permissions),
    )


def _token_from_request(request: Request) -> str | None:
    """从 Bearer 或会话 Cookie 提取令牌"""
    authorization = request.headers.get("authorization", "")
    if authorization.lower().startswith("bearer "):
        return authorization[7:].strip() or None

    return request.cookies.get(SESSION_COOKIE)


async def get_principal(request: Request) -> Principal:
    """当前主体 - 认证关闭时返回本地主体"""
    if not settings.auth.enabled:
        return DEV_PRINCIPAL

    token = _token_from_request(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未认证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        claims = await asyncio.to_thread(_decode_token, token)
        return _principal_from_claims(claims)
    except Exception:
        logger.warning("auth.token_invalid", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


def require_permission(permission: str):
    """权限依赖 - 未授权返回 403"""

    async def dependency(
        principal: Annotated[Principal, Depends(get_principal)],
    ) -> Principal:
        if "*" not in principal.permissions and permission not in principal.permissions:
            raise HTTPException(status_code=403, detail="权限不足")

        return principal

    return dependency


def _cookie_options() -> dict[str, Any]:
    """会话 Cookie 选项"""
    return {
        "httponly": True,
        "secure": settings.auth.cookie_secure,
        "samesite": "lax",
        "domain": settings.auth.cookie_domain or None,
    }


def _pkce_pair() -> tuple[str, str]:
    """PKCE verifier 与 challenge"""
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")

    return verifier, challenge


def _safe_next(value: str | None) -> str:
    """仅允许站内相对跳转"""
    if not value or not value.startswith("/") or value.startswith("//"):
        return "/"

    return value


def _auth_ready() -> None:
    """认证配置检查"""
    if not settings.auth.enabled:
        raise HTTPException(status_code=503, detail="认证未启用")

    if not settings.auth.client_id or not settings.auth.client_secret:
        raise HTTPException(status_code=503, detail="认证未配置")


# 认证路由
auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.get("/login", description="跳转 Casdoor 登录")
async def login(request: Request) -> RedirectResponse:
    """生成 state/nonce/PKCE 后跳转 Casdoor"""
    _auth_ready()

    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    verifier, challenge = _pkce_pair()
    next_url = _safe_next(request.query_params.get("next"))
    authorize_url, _, _, _ = _urls()

    params = {
        "response_type": "code",
        "client_id": settings.auth.client_id,
        "redirect_uri": settings.auth.redirect_uri,
        "scope": "openid profile email",
        "state": state,
        "nonce": nonce,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }

    response = RedirectResponse(
        f"{authorize_url}?{urlencode(params)}",
        status_code=status.HTTP_302_FOUND,
    )
    response.set_cookie(
        STATE_COOKIE,
        _serializer().dumps(
            {
                "state": state,
                "nonce": nonce,
                "verifier": verifier,
                "next": next_url,
            }
        ),
        max_age=STATE_TTL_SECONDS,
        path="/auth",
        **_cookie_options(),
    )

    return response


@auth_router.get("/callback", description="Casdoor 登录回调")
async def callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
) -> RedirectResponse:
    """校验 state, 换取令牌并写入会话 Cookie"""
    _auth_ready()

    raw_state = request.cookies.get(STATE_COOKIE)
    if not code or not state or not raw_state:
        raise HTTPException(status_code=400, detail="登录状态缺失")

    try:
        data = _serializer().loads(raw_state, max_age=STATE_TTL_SECONDS)
    except Exception:
        raise HTTPException(status_code=400, detail="登录状态无效") from None

    if not isinstance(data, dict) or not secrets.compare_digest(
        str(data.get("state", "")), state
    ):
        raise HTTPException(status_code=400, detail="登录状态不匹配")

    _, token_url, _, _ = _urls()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                token_url,
                data={
                    "grant_type": "authorization_code",
                    "client_id": settings.auth.client_id,
                    "client_secret": settings.auth.client_secret,
                    "code": code,
                    "redirect_uri": settings.auth.redirect_uri,
                    "code_verifier": str(data.get("verifier", "")),
                },
            )
            response.raise_for_status()
            tokens = response.json()
    except Exception:
        logger.warning("auth.token_exchange_failed", exc_info=True)
        raise HTTPException(status_code=502, detail="认证服务不可用") from None

    token = tokens.get("id_token") or tokens.get("access_token")
    if not isinstance(token, str) or not token:
        raise HTTPException(status_code=502, detail="认证服务未返回令牌")

    try:
        claims = await asyncio.to_thread(_decode_token, token)
    except Exception:
        logger.warning("auth.callback_token_invalid", exc_info=True)
        raise HTTPException(status_code=401, detail="登录令牌无效") from None

    nonce = data.get("nonce")
    if nonce and not secrets.compare_digest(str(claims.get("nonce", "")), str(nonce)):
        raise HTTPException(status_code=401, detail="登录 nonce 不匹配")

    _principal_from_claims(claims)

    next_url = _safe_next(str(data.get("next", "/")))
    expires_in = claims.get("exp", time.time() + 3600)
    max_age = max(60, int(float(expires_in) - time.time()))

    response = RedirectResponse(next_url, status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=max_age,
        path="/",
        **_cookie_options(),
    )
    response.delete_cookie(STATE_COOKIE, path="/auth")

    return response


@auth_router.get("/logout", description="登出并返回 Web")
async def logout_redirect(request: Request) -> RedirectResponse:
    """清除本地会话并跳转 Casdoor 登出"""
    _, _, _, logout_url = _urls()
    token = request.cookies.get(SESSION_COOKIE)

    params: dict[str, str] = {}
    if settings.auth.enabled:
        if settings.auth.post_logout_redirect_uri:
            params["post_logout_redirect_uri"] = settings.auth.post_logout_redirect_uri
        if token:
            params["id_token_hint"] = token

    target = f"{logout_url}?{urlencode(params)}" if params else "/"
    response = RedirectResponse(target, status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(SESSION_COOKIE, path="/")

    return response


@auth_router.post("/logout", description="清除登录会话")
async def logout() -> JSONResponse:
    """清除会话 Cookie"""
    response = JSONResponse({"code": 0, "message": "ok", "data": {}})
    response.delete_cookie(SESSION_COOKIE, path="/")

    return response


@auth_router.get("/me", description="当前登录用户")
async def me(
    principal: Annotated[Principal, Depends(get_principal)],
) -> dict[str, Any]:
    """返回当前主体与权限"""
    return {
        "code": 0,
        "message": "ok",
        "data": {
            "user_id": principal.user_id,
            "tenant_id": principal.tenant_id,
            "email": principal.email,
            "name": principal.name,
            "roles": list(principal.roles),
            "permissions": sorted(principal.permissions),
        },
    }
