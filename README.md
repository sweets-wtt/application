# application

## 概览

- 用途：框架
- 状态：应用

## 架构

```text
application（根项目）
├── mise（环境管理）
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
│   └── 工作区
│       └── 运行时与依赖管理：uv
│           ├── 测试
│           │   ├── 测试框架：pytest → uv
│           │   ├── 异步测试：pytest-asyncio → uv
│           │   └── 覆盖率：pytest-cov → uv
│           ├── HTTP
│           │   └── 客户端：httpx2 → uv
│           └── 代码
│               ├── 代码检查：ruff → uv
│               └── 类型检查：ty → uv
│       └── 运行时与依赖管理：bun
│           ├── 测试
│           │   └── 测试框架：vitest → bun
│           └── 代码
│               ├── 代码检查：oxlint → bun
│               ├── 代码格式化：oxfmt → bun
│               └── 类型检查：typescript → bun
├── renovate（依赖更新）→ mise
├── github（GitHub）
├── podman（容器平台）
│   └── 平台
│       └── caddy（入口代理）
├── packages（共享包）
│   ├── python
│   │   ├── contracts（契约模型）→ pydantic
│   │   └── log（结构化日志）→ structlog
│   └── typescript
│       ├── contracts（契约客户端）→ vue-query / msw / zod
│       ├── log（结构化日志）→ consola
│       └── session（状态与会话）→ zod
└── apps（应用）
    └── server（Server 应用）
        ├── fastapi（web 框架）
        ├── granian（ASGI 服务器）
        ├── pydantic-settings（配置管理）
        └── schemathesis（契约测试）
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
│   └── web                          # Web
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
├── packages                         # 共享包
│   ├── python                       # Python
│   │   ├── contracts                # 契约模型
│   │   ├── log                      # 结构化日志
│   │   └── workflow                 # 工作流
│   └── typescript                   # TypeScript
│       ├── contracts                # 契约客户端
│       ├── log                      # 结构化日志
│       └── session                  # 状态与会话
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
├── lefthook.yaml                    # 钩子管理
├── mise.lock                        # 工具版本
├── mise.toml                        # 开发环境与任务
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
