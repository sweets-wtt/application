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
| [typos](https://github.com/crate-ci/typos) | 拼写检查 |
| [oxfmt](https://oxc.rs/docs/guide/usage/formatter) | 代码格式化 |
| [ripgrep](https://github.com/BurntSushi/ripgrep) | 正则搜索 |
| [cocogitto](https://docs.cocogitto.io/) | 提交检查 |

## 命令

| 命令 | 用途 |
| --- | --- |
| `mise install --locked` | 安装工具 |
| `moon run :<task>` / `moon ci` | 运行任务 |
| `moon run :lint` | 代码检查 |

## 结构

```text
.
├── .moon                  # 任务编排
│   ├── tasks              # 任务目录
│   │   └── all.yaml       # 全局任务
│   ├── toolchains.yaml    # 工具链
│   └── workspace.yaml     # 工作区
├── .editorconfig          # 代码风格
├── .gitattributes         # Git 属性
├── .gitignore             # Git 忽略
├── .typos.toml            # 拼写检查
├── cog.toml               # 提交检查
├── mise.lock              # 工具版本
├── mise.toml              # 开发环境
└── README.md              # 项目说明
```
