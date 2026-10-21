# application

## 架构

```text
根: application
├── 环境管理: mise
│   ├── 任务运行: task
│   ├── 配置校验: config-file-validator
│   ├── 配置格式: dprint
│   ├── 拼写检查: typos
│   ├── 提交检查: cocogitto
│   ├── 钩子管理: lefthook
│   ├── 安全扫描: trivy
│   ├── 兼容性检查: oasdiff
│   ├── HTTP 契约: vacuum
│   ├── 本地编排: process-compose
│   ├── 验收: hurl
│   ├── Python 运行时: python
│   ├── Python 依赖管理: uv
│   │   ├── 代码检查: ruff
│   │   └── 类型检查: ty
│   ├── TypeScript 运行时: node
│   └── TypeScript 依赖管理: bun
│       ├── 代码检查: oxlint
│       └── 类型检查: tsc
└── 共享包: packages
    └── Python 包: python
        ├── 契约模型: contracts
        ├── 结构化日志: log
        ├── 数据库会话: db
        ├── 缓存: cache
        ├── 对象存储: storage
        └── 工作流: workflow
```

## 结构

```text
.
├── contracts               # 契约
│  └── http                 # HTTP
│     ├── schemas           # 模型定义
│     ├── openapi.yaml      # OpenAPI
│     └── vacuum.yaml       # 规则集
├── infra                   # 设施
│  ├── garage               # 对象存储
│  │  └── garage.toml       # Garage 配置
│  ├── observe              # 可观测
│  │  └── collector.yaml    # Collector 配置
│  ├── postgresql           # 数据库
│  │  └── init.sql          # 初始化脚本
│  ├── traefik              # 入口
│  │  └── dynamic.yaml      # 动态配置
│  ├── .env.example         # 平台配置
│  └── test.hurl            # hurl 验收
├── packages                 # 共享包
│  └── python                # Python 包
├── .cfv.toml               # 校验配置
├── .editorconfig           # 代码风格
├── .gitattributes          # Git 属性
├── .gitignore              # Git 忽略
├── .oxlintrc.jsonc         # Oxlint 配置
├── .typos.toml             # 拼写检查
├── bun.lock                # TypeScript 依赖
├── dprint.jsonc            # 配置格式
├── lefthook.yaml           # 钩子管理
├── mise.lock               # 工具锁定
├── mise.toml               # 环境管理
├── package.json            # TypeScript 配置
├── process-compose.yaml    # 本地编排
├── pyproject.toml          # Python 配置
├── trivy-secret.yaml       # 密钥规则
├── trivy.yaml              # 安全扫描
├── tsconfig.base.json      # TypeScript 基础配置
├── tsconfig.json           # TypeScript 项目配置
├── uv.lock                 # Python 依赖
├── README.md               # 项目说明
└── Taskfile.yaml           # 任务定义
```
