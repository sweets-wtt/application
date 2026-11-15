# Infra

部署与本地编排配置，公网入口由 Web 镜像内置的 Caddy 承担，统一终止 TLS 并托管静态资源，站点配置位于本目录

## 结构

```text
infra/              # 部署配置
├── secrets/        # 部署密钥
├── .env.example    # 变量示例
├── Caddyfile       # 入口配置
├── compose.yaml    # 容器编排
└── README.md       # 部署说明
```

空目录仅在需要时创建，文件均需实际存在

## 职责

* `compose.yaml`：编排 `api` 与 `web`，划分 `edge` 与 `internal` 网络
* `.env.example`：列出 compose 与前端构建所需变量，不包含真实密钥
* `Caddyfile`：随 Web 镜像构建的入口配置，负责 HTTPS、ACME 证书与站点路由；安全头、压缩与访问日志抽为 `site` 片段复用

## 注意事项

* 本地使用前复制 `.env.example` 为 `.env`，真实 `.env` 不提交
* `AUTH_DOMAIN` 是历史命名，当前仅作为站点域名使用，实际站点为 `web.<AUTH_DOMAIN>`
* `SERVER_IMAGE` 与 `WEB_IMAGE` 生产环境应使用不可变 tag 或 digest，避免 `latest`
* `api` 只加入 `internal` 网络；`web` 同时加入 `edge` 与 `internal`；只有 `web` 暴露公网端口
* `api` 服务只声明镜像，不负责构建；启动编排前先执行 `task build-image`
* Dockerfile 保留在 `apps/`，由 compose 通过 `context` 与 `dockerfile` 引用
* `VITE_*` 是 Web 构建时变量，修改后需要重新构建 Web 镜像
* Web 镜像内置 Caddy，容器内 `:8081` 仅用于健康检查，不对外发布端口
* `Caddyfile` 通过 `.dockerignore` 的 `!infra/Caddyfile` 例外进入构建上下文，删除该例外会导致 Web 镜像构建失败
* 新增站点时在 `Caddyfile` 追加站点块并 `import site`，不要复制安全头、压缩与日志配置
* 证书与 Caddy 运行数据存放在 `caddy-data` 卷，重建容器不会重新签发证书
* 当前没有数据库服务；server 启动不依赖数据库
* 本地开发差异写入 `compose.override.yaml`，不要用 profiles 模拟环境
* 拆多个 compose 文件时使用 `include`，不要用多个 `-f`，避免相对路径解析错误
* 生产密钥通过 sops、age 或部署平台注入，不要写进镜像
* 修改编排或代理配置后运行 `task check-compose`

## 命名约定

| 对象     | 规则                 | 示例                                               |
| -------- | -------------------- | -------------------------------------------------- |
| 编排文件 | `compose.yaml`       | 不使用 `docker-compose.yml`                        |
| 环境叠加 | `compose.<env>.yaml` | `compose.override.yaml`、`compose.production.yaml` |
| 代理配置 | `Caddyfile`          | 位于 `infra/`，随 Web 镜像构建                     |
| 变量模板 | `.env.example`       | 不使用 `.env.template`                             |
| 密钥目录 | `secrets/`           | 内容不入库                                         |

## 常用命令

```bash
# 准备本地变量
cp infra/.env.example infra/.env

# 构建镜像
mise exec -- task build-image

# 启动 / 停止本地服务
mise exec -- task compose-up
mise exec -- task compose-down

# 校验 compose 配置
mise exec -- task check-compose

# 扫描镜像与配置漏洞
mise exec -- task scan-vuln
```

## 修改流程

1. 修改 `compose.yaml`、`Caddyfile` 或 `.env.example`
2. 同步更新根 README 与相关应用 README
3. 运行 `task check-compose`
4. 本地执行 `task build-image`、`task compose-up` 验证服务可启动
5. 生产部署使用固定镜像 tag/digest 与外部密钥
