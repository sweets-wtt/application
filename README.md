# application

## 技术架构

```text
根: application
├── 环境管理: mise
│   ├── 任务管理: task
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
    │   ├── 运行时: uv
    │   ├── web 框架: fastapi
    │   ├── ASGI 服务器: granian
    │   ├── 配置管理: pydantic-settings
    │   ├── 数据校验: pydantic
    │   ├── 结构化日志: structlog
    │   └── 契约测试: schemathesis
    └── web
        ├── 运行时: bun
        ├── 框架: vue
        ├── 构建工具: vite
        ├── 语言: typescript
        ├── 路由: vue-router
        ├── 状态管理: pinia
        ├── 状态持久化: pinia-plugin-persistedstate
        ├── 数据请求: @tanstack/vue-query
        ├── 组合式工具: @vueuse/core
        ├── 契约客户端: orval
        ├── 模式校验: zod
        ├── 样式: unocss
        ├── 图标: @iconify-json/carbon
        ├── 组件库: reka-ui
        └── 结构化日志: consola
```

## 项目结构

```text
.                       # 根级目录
├── .github/            # 持续集成
├── apps/               # 应用目录
│   ├── server/         # 服务应用
│   └── web/            # 前端应用
├── contracts/          # 契约目录
├── infra/              # 服务编排
├── .containerignore    # 构建忽略
├── .editorconfig       # 代码风格
├── .gitattributes      # 版本属性
├── .gitignore          # 版本忽略
├── .gitleaks.toml      # 密钥扫描
├── .oxfmtrc.jsonc      # 格式配置
├── .oxlintrc.jsonc     # 检查配置
├── .python-version     # 语言版本
├── bun.lock            # 前端依赖
├── cog.toml            # 提交规范
├── dprint.jsonc        # 代码格式
├── Taskfile.yaml       # 任务配方
├── lefthook.yaml       # 钩子管理
├── mise.lock           # 工具版本
├── mise.toml           # 开发环境
├── package.json        # 包体配置
├── pyproject.toml      # 工作区根
├── renovate.jsonc      # 依赖更新
├── ruff.toml           # 后端检查
├── ty.toml             # 类型检查
├── typos.toml          # 拼写检查
├── uv.lock             # 后端依赖
├── zizmor.yaml         # 安全审计
└── README.md           # 项目说明
```
