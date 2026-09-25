# application

## 概览

- 用途：框架
- 状态：服务

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
│   └── 测试
│       └── HTTP 测试：hurl → docker
├── renovate（依赖更新）→ mise
├── github（GitHub）
└── docker（容器平台）
    ├── 数据
    │   ├── postgresql（关系数据库）
    │   ├── pgbouncer（连接池）→ postgresql
    │   ├── valkey（缓存）
    │   └── garage（对象存储）
    └── 备份
        └── restic（归档备份）→ postgresql / garage
```

## 结构

```text
.
├── .github                          # 持续集成
│   └── workflows                    # 工作流
│       ├── ci.yaml                  # 持续集成
│       └── release.yaml             # 版本发行
├── contracts                        # 契约
│   └── http                         # HTTP
│       ├── openapi.yaml             # 接口规范
│       └── vacuum.yaml              # 契约检查
├── infra                            # 服务编排
│   ├── garage                       # Garage
│   ├── pgbouncer                    # PgBouncer
│   ├── postgresql                   # PostgreSQL
│   ├── valkey                       # Valkey
│   ├── .env.example                 # 环境变量
│   └── compose.yaml                 # 容器编排
├── .editorconfig                    # 代码风格
├── .gitattributes                   # Git 属性
├── .gitignore                       # Git 忽略
├── .gitleaks.toml                   # 密钥扫描
├── .release-please-manifest.json    # 版本清单
├── .typos.toml                      # 拼写检查
├── cog.toml                         # 提交检查
├── dprint.jsonc                     # 代码格式
├── justfile                         # 任务运行
├── lefthook.yaml                    # 钩子管理
├── mise.lock                        # 工具版本
├── mise.toml                        # 开发环境
├── renovate.jsonc                   # 依赖更新
├── zizmor.yaml                      # 安全审计
└── README.md                        # 项目说明
```
