# application

## 概览

- 用途：框架
- 状态：应用

## 架构

```text
application（根项目）
├── mise（环境管理）
│   ├── 任务运行：just
│   ├── 代码
│   │   ├── 代码格式：dprint
│   │   └── 拼写检查：typos
│   ├── 提交
│   │   ├── 提交检查：cocogitto
│   │   └── 钩子管理：lefthook → cocogitto
│   ├── 安全
│   │   ├── 密钥扫描：gitleaks
│   │   ├── 漏洞扫描：trivy
│   │   ├── 语法检查：actionlint → github
│   │   └── 工作流审计：zizmor → github
│   ├── 契约
│   │   ├── 契约检查：vacuum → openapi
│   │   └── 兼容检查：oasdiff → openapi
│   ├── 测试
│   │   └── HTTP 测试：hurl → docker
│   └── 工作区
│       ├── 运行时：python
│       ├── 依赖管理：uv → python
│       │   └── 代码
│       │       ├── 代码检查：ruff → uv
│       │       └── 类型检查：ty → uv
│       ├── 运行时：node
│       └── 依赖管理：bun → node
│           └── 代码
│               ├── 代码检查：oxlint → bun
│               └── 代码格式化：oxfmt → bun
├── renovate（依赖更新）→ mise
├── github（GitHub）
├── docker（容器平台）
│   ├── 数据
│   │   ├── postgresql（关系数据库）
│   │   ├── pgbouncer（连接池）→ postgresql
│   │   ├── valkey（缓存）
│   │   └── garage（对象存储）
│   ├── 平台
│   │   ├── hatchet（工作流）→ postgresql / pgbouncer
│   │   ├── authentik（身份认证）→ postgresql
│   │   └── traefik（入口代理）→ authentik
│   ├── 观测
│   │   ├── collector（遥测采集）→ postgresql / openobserve
│   │   └── openobserve（观测存储）→ garage
│   └── 备份
│       └── restic（归档备份）→ postgresql / garage
├── packages（共享包）
│   ├── python
│   │   ├── cache（缓存）→ valkey
│   │   ├── contracts（契约模型）→ pydantic
│   │   ├── db（数据库会话）→ sqlalchemy / asyncpg
│   │   ├── log（结构化日志）→ structlog
│   │   ├── storage（对象存储）→ aiobotocore
│   │   └── workflow（工作流）→ hatchet-sdk
│   └── typescript
│       ├── auth（会话与令牌）→ state / zod
│       ├── contracts（契约客户端）→ vue-query / msw / zod
│       ├── log（结构化日志）→ consola
│       ├── realtime（实时）→ contracts / zod
│       └── state（持久化状态）→ zod
└── apps（应用）
    └── server（Server 应用）→ contracts / log
        ├── api → docker
        └── worker → docker
```

## 结构

```text
.
├── .github                          # 持续集成
│   └── workflows                    # 工作流
│       ├── ci.yaml                  # 持续集成
│       └── release.yaml             # 版本发行
├── apps                             # 应用
│   └── server                       # Server
├── contracts                        # 契约
│   └── http                         # HTTP
│       ├── openapi.yaml             # 接口规范
│       └── vacuum.yaml              # 契约检查
├── infra                            # 服务编排
│   ├── authentik                    # authentik
│   ├── garage                       # Garage
│   ├── hatchet                      # Hatchet
│   ├── observe                      # OpenObserve
│   ├── pgbouncer                    # PgBouncer
│   ├── postgresql                   # PostgreSQL
│   ├── traefik                      # Traefik
│   ├── valkey                       # Valkey
│   ├── .env.example                 # 环境变量
│   └── compose.yaml                 # 容器编排
├── packages                         # 共享包
│   ├── python                       # Python
│   │   ├── cache                    # 缓存
│   │   ├── contracts                # 契约模型
│   │   ├── db                       # 数据库会话
│   │   ├── log                      # 结构化日志
│   │   ├── storage                  # 对象存储
│   │   └── workflow                 # 工作流
│   └── typescript                   # TypeScript
│       ├── auth                     # 会话与令牌
│       ├── contracts                # 契约客户端
│       ├── log                      # 结构化日志
│       ├── realtime                 # 实时
│       └── state                    # 持久化状态
├── tests                            # 测试
│   └── docker                       # 容器
│       ├── observe.hurl             # 观测验收
│       ├── oidc.hurl                # OIDC 验收
│       └── tls.hurl                 # TLS 验收
├── .editorconfig                    # 代码风格
├── .gitattributes                   # Git 属性
├── .gitignore                       # Git 忽略
├── .gitleaks.toml                   # 密钥扫描
├── .oxlintrc.json                   # JavaScript 代码检查
├── .release-please-manifest.json    # 版本清单
├── .typos.toml                      # 拼写检查
├── bun.lock                         # JavaScript 依赖
├── cog.toml                         # 提交检查
├── dprint.jsonc                     # 代码格式
├── justfile                         # 任务运行
├── lefthook.yaml                    # 钩子管理
├── mise.lock                        # 工具版本
├── mise.toml                        # 开发环境
├── package.json                     # JavaScript 包
├── pyproject.toml                   # Python 配置
├── renovate.jsonc                   # 依赖更新
├── schemathesis.toml                # 契约模糊测试
├── tsconfig.base.json               # JavaScript 基础
├── tsconfig.json                    # JavaScript 配置
├── uv.lock                          # Python 依赖
├── zizmor.yaml                      # 安全审计
└── README.md                        # 项目说明
```
