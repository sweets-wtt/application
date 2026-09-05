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

## 命令

| 命令 | 用途 |
| --- | --- |
| `mise install --locked` | 安装工具 |
| `moon run :<task>` / `moon ci` | 运行任务 |

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
├── mise.lock              # 工具版本
├── mise.toml              # 开发环境
└── README.md              # 项目说明
```
