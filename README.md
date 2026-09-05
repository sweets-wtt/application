# application

## 概览

- 用途：框架模板
- 状态：工具链

## 技术

### 工具链

| 名称 | 说明 |
| --- | --- |
| [mise](https://mise.jdx.dev/) | 环境管理 |
| [moon](https://moonrepo.dev/docs) | 构建系统 |
| [ripgrep](https://github.com/BurntSushi/ripgrep) | 正则搜索 |
| [typos](https://github.com/crate-ci/typos) | 拼写检查 |
| [lychee](https://lychee.cli.rs/) | 链接检查 |
| [cocogitto](https://docs.cocogitto.io/) | 提交检查 |
| [zizmor](https://docs.zizmor.sh/) | 安全审计 |
| [actionlint](https://rhysd.github.io/actionlint/) | 语法检查 |
| [sops](https://getsops.io/) | 密钥加密 |
| [age](https://age-encryption.org/) | 加密工具 |
| [gitleaks](https://github.com/gitleaks/gitleaks) | 密钥扫描 |
| [trivy](https://trivy.dev/) | 漏洞扫描 |
| [config-file-validator](https://github.com/Boeing/config-file-validator) | 配置校验 |

## 命令

| 命令 | 用途 |
| --- | --- |
| `mise install --locked` | 安装工具 |
| `moon run :<task>` / `moon ci` | 运行任务 |

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
├── .editorconfig                    # 代码风格
├── .gitattributes                   # Git 属性
├── .gitignore                       # Git 忽略
├── .gitleaks.toml                   # 密钥扫描
├── .release-please-manifest.json    # 版本清单
├── .sops.yaml                       # 密钥加密
├── .typos.toml                      # 拼写检查
├── cog.toml                         # 提交检查
├── lychee.toml                      # 链接检查
├── mise.lock                        # 工具版本
├── mise.toml                        # 开发环境
├── renovate.json5                   # 依赖更新
├── trivy.yaml                       # 漏洞扫描
├── zizmor.yaml                      # 安全审计
└── README.md                        # 项目说明
```
