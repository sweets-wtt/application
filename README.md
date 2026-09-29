# application

## 概览

- 用途: 框架
- 状态: 服务

## 架构

```text
根: application
├── 环境管理: mise
│   ├── 代码格式: dprint
│   ├── 拼写检查: typos
│   ├── 提交检查: cocogitto
│   ├── 钩子管理: lefthook → cocogitto
│   ├── 语法检查: actionlint → github
│   ├── 工作流审计: zizmor → github
│   ├── 密钥扫描: gitleaks
│   ├── 漏洞扫描: trivy
│   └── HTTP 测试: hurl → docker
├── GitHub: github
├── 依赖更新: renovate → mise
├── 接口规范: openapi
│   ├── 契约检查: vacuum → openapi
│   └── 兼容检查: oasdiff → openapi
└── 容器平台: docker
    ├── 归档备份: restic → postgresql / garage
    ├── 关系数据库: postgresql
    ├── 连接池: pgbouncer → postgresql
    ├── 数据缓存: valkey
    ├── 对象存储: garage
    └── 工作流: hatchet → postgresql / pgbouncer
```

## 结构

```text
.
├── .github                 # GitHub
│   └── workflows           # 工作流
│       └── ci.yaml         # 持续集成
├── contracts               # 契约
│   └── http                # HTTP
│       ├── paths           # 接口定义
│       ├── schemas         # 数据模式
│       ├── openapi.yaml    # 接口规范
│       └── vacuum.yaml     # 契约检查
├── infra                   # 服务编排
│   ├── garage              # Garage
│   ├── hatchet             # Hatchet
│   ├── pgbouncer           # PgBouncer
│   ├── postgresql          # PostgreSQL
│   ├── valkey              # Valkey
│   ├── .env.example        # 环境变量
│   └── compose.yaml        # 容器编排
├── .dockerignore           # 构建排除
├── .editorconfig           # 代码风格
├── .gitattributes          # Git 属性
├── .gitignore              # Git 忽略
├── .gitleaks.toml          # 密钥扫描
├── .typos.toml             # 拼写检查
├── docker-bake.hcl         # 镜像构建
├── dprint.jsonc            # 代码格式
├── lefthook.yaml           # 钩子管理
├── mise.lock               # 工具版本
├── mise.toml               # 环境管理
├── renovate.jsonc          # 依赖更新
└── README.md               # 项目说明
```
