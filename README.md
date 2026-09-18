# application

## 概览

- 用途：框架
- 状态：工具链

## 架构

```mermaid
flowchart TD
    application["application（根项目）"]
    application -->|工具链| mise["mise（环境管理）"]
    mise -->|执行环境| just["just（任务运行）"]
```

## 结构

```text
.
├── .editorconfig     # 代码风格
├── .gitattributes    # Git 属性
├── .gitignore        # Git 忽略
├── justfile          # 任务运行
├── mise.lock         # 工具版本
├── mise.toml         # 开发环境
└── README.md         # 项目说明
```
