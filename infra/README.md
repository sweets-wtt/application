# Infra

部署与本地编排配置生产入口由 Caddy 统一终止 TLS，Web 由 Nginx 托管并反代 API

## 结构

```text
infra/              # 部署配置
├── .env.example    # 环境变量示例
├── compose.yaml    # 容器编排
└── Caddyfile       # 入口代理
```

## 职责

* `Caddyfile`：唯一公网入口，负责 HTTPS、ACME 证书与反向代理到 `web:80`
* `compose.yaml`：编排 `caddy`、`api`、`web`，划分 `edge` 与 `internal` 网络
* `.env.example`：列出 compose 与前端构建所需变量，不包含真实密钥

## 注意事项

* 本地使用前复制 `.env.example` 为 `.env`，真实 `.env` 不提交
* `AUTH_DOMAIN` 是历史命名，当前仅作为站点域名使用
* `SERVER_IMAGE` 与 `WEB_IMAGE` 生产环境应使用不可变 tag 或 digest，避免 `latest`
* `api` 只加入 `internal` 网络；`web` 同时加入 `edge` 与 `internal`；只有 Caddy 暴露公网端口
* `api` 服务只声明镜像，不负责构建；启动编排前先执行 `just build-image`
* `VITE_*` 是 Web 构建时变量，修改后需要重新构建 Web 镜像
* 当前没有数据库服务；server 启动不依赖数据库
* 修改编排或代理配置后运行 `just check-compose`
* 生产密钥应通过容器环境变量、密钥管理或部署平台注入，不要写进镜像

## 常用命令

```bash
# 准备本地变量
cp infra/.env.example infra/.env

# 构建镜像
mise exec -- just build-image

# 启动 / 停止本地服务
mise exec -- just up
mise exec -- just down

# 校验 compose 配置
mise exec -- just check-compose

# 扫描镜像与配置漏洞
mise exec -- just audit
```

## 修改流程

1. 修改 `compose.yaml`、`Caddyfile` 或 `.env.example`
2. 同步更新根 README 与相关应用 README
3. 运行 `just check-compose`
4. 本地执行 `just build-image`、`just up` 验证服务可启动
5. 生产部署使用固定镜像 tag/digest 与外部密钥
