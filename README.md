# application

## 概览

- 用途：框架
- 状态：应用

## 架构

```text
根: application
├── 环境管理: mise
│   ├── 任务管理: just
│   ├── 代码格式: dprint
│   ├── 拼写检查: typos
│   ├── 提交检查: cocogitto
│   ├── 钩子管理: lefthook
│   ├── 密钥扫描: gitleaks
│   ├── 漏洞扫描: trivy
│   ├── 语法检查: actionlint
│   ├── 工作流审计: zizmor
│   ├── 契约检查: vacuum
│   ├── 兼容检查: oasdiff
│   ├── 运行时管理: uv
│   └── 运行时管理: bun
├── 依赖更新: renovate
├── 持续集成: github
├── 容器平台: podman
│   └── 入口代理: caddy
├── Python 工具链
│   ├── 测试框架: pytest
│   ├── 异步测试: pytest-asyncio
│   ├── 覆盖率: pytest-cov
│   ├── 代码检查: ruff
│   └── 类型检查: ty
├── TypeScript 工具链
│   ├── 测试框架: vitest
│   ├── 代码检查: oxlint
│   ├── 代码格式化: oxfmt
│   └── 类型检查: typescript
└── 应用: apps
    ├── server
    │   ├── web 框架: fastapi
    │   ├── ASGI 服务器: granian
    │   ├── 配置管理: pydantic-settings
    │   ├── 结构化日志: structlog
    │   ├── 契约模型: pydantic
    │   ├── 限流: slowapi
    │   └── 契约测试: schemathesis
    └── web
        ├── 框架: vue
        ├── 路由: vue-router
        ├── 状态管理: pinia
        ├── 契约客户端: vue-query
        ├── 模式校验: zod
        ├── 组件库: reka-ui
        └── 结构化日志: consola
```

## 结构

```text
.
├── .github                          # 持续集成
│   ├── actions                      # 复合动作
│   │   └── setup                    # 环境准备
│   │       └── action.yml           # 检出与工具链
│   └── workflows                    # 工作流
│       ├── ci.yaml                  # 持续集成
│       └── release.yaml             # 版本发行
├── apps                             # 应用
│   ├── server                       # Server
│   │   ├── .python-version          # Python 版本
│   │   ├── pyproject.toml           # Python 项目配置（工作区成员）
│   │   ├── schemathesis.toml        # 契约模糊测试
│   │   └── src/server               # 源码（含契约生成物）
│   └── web                          # Web
│       ├── orval.config.ts          # 契约客户端生成
│       └── src                      # 源码（含契约生成物）
├── contracts                         # 契约
│   └── http                         # HTTP
│       ├── components               # 组件（参数/请求体/响应/模式）
│       ├── dist                     # 打包制品
│       │   └── openapi.yaml         # 接口规范（生成）
│       ├── openapi.yaml             # 契约入口
│       ├── paths                    # 路径（按资源域一文件）
│       └── vacuum.yaml              # 契约检查
├── infra                            # 服务编排
│   ├── Caddyfile                    # 入口代理配置
│   ├── compose.yaml                 # 容器编排
│   └── .env.example                 # 环境变量
├── .containerignore                 # 构建忽略
├── .editorconfig                    # 代码风格
├── .gitattributes                   # Git 属性
├── .gitignore                       # Git 忽略
├── .gitleaks.toml                   # 密钥扫描
├── .oxlintrc.jsonc                  # JavaScript 代码检查
├── .typos.toml                      # 拼写检查
├── bun.lock                         # JavaScript 依赖
├── cog.toml                         # 提交检查
├── dprint.jsonc                     # 代码格式
├── justfile                         # 任务配方
├── lefthook.yaml                    # 钩子管理
├── mise.lock                        # 工具版本
├── mise.toml                        # 开发环境（工具链）
├── package.json                     # JavaScript 包
├── pyproject.toml                   # Python 工作区根（含仓库级工具）
├── renovate.jsonc                   # 依赖更新
├── uv.lock                          # Python 依赖（工作区统一）
├── zizmor.yaml                      # 安全审计
└── README.md                        # 项目说明
```
