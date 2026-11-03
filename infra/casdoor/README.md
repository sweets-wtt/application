# Casdoor 本地配置

Casdoor 容器由 `infra/compose.yaml` 启动，数据库使用现有 PostgreSQL 的 `casdoor` 库。

首次启动时，容器会把 `init_data.template.yaml` 渲染为初始数据，创建：

- Organization：`application`
- Application：`app-web`
- 角色：`admin`、`editor`、`viewer`

## 1. 准备环境变量

在 `infra/.env` 中确认以下值已填写：

```dotenv
CASDOOR_ADMIN_PASSWORD=       # 首次启动的 admin 密码
CASDOOR_CLIENT_ID=app-web     # Web 应用 Client ID
CASDOOR_CLIENT_SECRET=        # Web 应用 Client Secret
AUTH_STATE_SECRET=            # 登录 state 签名密钥
```

`CASDOOR_CLIENT_ID` / `CASDOOR_CLIENT_SECRET` 会写入初始化数据，必须与 FastAPI 配置一致。修改后重启 `api`。

## 2. 启动

```bash
mise run up
```

访问：

- Casdoor 控制台：`https://auth.<AUTH_DOMAIN>`
- Web：`https://web.<AUTH_DOMAIN>`

使用 `built-in/admin` 和 `CASDOOR_ADMIN_PASSWORD` 登录。

> 已有 PostgreSQL 数据卷时，`casdoor-db` 一次性服务会自动创建 `casdoor` 库。
>
> 如果初始化数据没有生效，检查 `podman logs application-casdoor-1`，或手动在 Casdoor 控制台创建应用。

## 3. 登录流程

```text
Web 未登录
  → /auth/login
  → Casdoor 登录/注册页
  → /auth/callback
  → FastAPI 换取令牌并写入 HttpOnly Cookie
  → 回到 Web
```

Casdoor 应用已预置回调地址：

```text
https://web.<AUTH_DOMAIN>/auth/callback
```

如果修改了域名，需要同步修改 `init_data.template.yaml` 或控制台中的 Redirect URLs。

## 4. 角色与权限

| 角色     | 权限                                                                                                      |
| -------- | --------------------------------------------------------------------------------------------------------- |
| `admin`  | 全部权限                                                                                                  |
| `editor` | `workflow:read`、`workflow:write`、`storage:read`、`storage:write`、`realtime:connect`、`telemetry:write` |
| `viewer` | `workflow:read`、`storage:read`、`realtime:connect`、`telemetry:write`                                    |

FastAPI 会从令牌的 `roles` 声明和 `isAdmin` 声明计算权限。若 Casdoor 未把角色写入令牌，需要在应用配置中补充自定义 claim，或先使用 `isAdmin` 区分管理员。

## 5. 生产注意

- 不要把 Casdoor 管理台直接暴露到公网；加 IP 白名单、VPN 或独立内部域名。
- 使用强 `CASDOOR_ADMIN_PASSWORD`，并启用 MFA。
- `CASDOOR_CLIENT_SECRET`、`AUTH_STATE_SECRET` 通过秘密管理注入，不提交到 Git。
- 生产必须使用 HTTPS，`APP_AUTH__COOKIE_SECURE=true`。
