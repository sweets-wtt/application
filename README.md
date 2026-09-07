# application

## 概览

- 用途：框架模板
- 状态：语言

## 技术

### 工具链

| 名称 | 说明 |
| --- | --- |
| [mise](https://mise.jdx.dev/) | 环境管理 |
| [moon](https://moonrepo.dev/docs) | 构建系统 |
| [typos](https://github.com/crate-ci/typos) | 拼写检查 |
| [oxfmt](https://oxc.rs/docs/guide/usage/formatter) | 代码格式化 |
| [ripgrep](https://github.com/BurntSushi/ripgrep) | 正则搜索 |
| [cocogitto](https://docs.cocogitto.io/) | 提交检查 |
| [zizmor](https://docs.zizmor.sh/) | 安全审计 |
| [lychee](https://lychee.cli.rs/) | 链接检查 |
| [actionlint](https://rhysd.github.io/actionlint/) | 语法检查 |
| [gitleaks](https://github.com/gitleaks/gitleaks) | 密钥扫描 |
| [trivy](https://trivy.dev/) | 漏洞扫描 |
| [config-file-validator](https://github.com/Boeing/config-file-validator) | 配置校验 |
| [sops](https://getsops.io/) | 密钥加密 |
| [age](https://age-encryption.org/) | 加密工具 |
| [Hurl](https://hurl.dev/) | HTTP 测试 |
| [Python](https://www.python.org/) | Python 运行时 |
| [uv](https://docs.astral.sh/uv/) | 依赖管理 |
| [Ruff](https://docs.astral.sh/ruff/) | 代码检查 |
| [ty](https://docs.astral.sh/ty/) | 类型检查 |
| [Node.js](https://nodejs.org/) | JavaScript 运行时 |
| [Bun](https://bun.com/) | 包管理 |
| [oxlint](https://oxc.rs/docs/guide/usage/linter) | 代码检查 |

### 契约

| 名称 | 说明 |
| --- | --- |
| [OpenAPI](https://spec.openapis.org/) | 接口规范 |
| [vacuum](https://quobix.com/vacuum/) | 契约检查 |
| [oasdiff](https://github.com/tufin/oasdiff) | 兼容检查 |

### 平台

| 名称 | 说明 |
| --- | --- |
| [Docker Compose](https://docs.docker.com/compose/) | 服务编排 |
| [Docker Bake](https://docs.docker.com/build/bake/) | 构建编排 |

## 命令

| 命令 | 用途 |
| --- | --- |
| `mise install --locked` | 安装工具 |
| `moon run :<task>` / `moon ci` | 运行任务 |
| `moon run :lint` | 代码检查 |

## 结构

```text
.
├── .github                          # 持续集成
│   └── workflows                    # 工作流
│       ├── ci.yaml                  # 持续集成
│       ├── ops.yaml                 # 定时运维
│       └── release.yaml             # 版本发行
├── .moon                            # 任务编排
│   ├── tasks                        # 任务目录
│   │   └── all.yaml                 # 全局任务
│   ├── toolchains.yaml              # 工具链
│   └── workspace.yaml               # 工作区
├── contracts                        # 契约
│   └── http                         # HTTP
│       ├── openapi.yaml             # 接口规范
│       └── vacuum.yaml              # 契约检查
├── infra                            # 服务编排
│   ├── .env.example                 # 环境变量
│   └── compose.yaml                 # 平台编排
├── .editorconfig                    # 代码风格
├── .gitattributes                   # Git 属性
├── .gitignore                       # Git 忽略
├── .gitleaks.toml                   # 密钥扫描
├── .release-please-manifest.json    # 版本清单
├── .sops.yaml                       # 密钥加密
├── .typos.toml                      # 拼写检查
├── .oxlintrc.json                   # 代码检查
├── bun.lock                         # TS 依赖
├── bunfig.toml                      # Bun 配置
├── cog.toml                         # 提交检查
├── docker-bake.hcl                  # 构建编排
├── lychee.toml                      # 链接检查
├── mise.lock                        # 工具版本
├── mise.toml                        # 开发环境
├── package.json                     # TS 包
├── pyproject.toml                   # PY 配置
├── renovate.json5                   # 依赖更新
├── trivy.yaml                       # 漏洞扫描
├── tsconfig.base.json               # TS 基础
├── tsconfig.json                    # TS 配置
├── uv.lock                          # PY 依赖
├── zizmor.yaml                      # 安全审计
└── README.md                        # 项目说明
```
