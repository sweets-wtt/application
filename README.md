# application

## 概览

- 用途：框架
- 状态：工具链

## 架构

```text
application（根项目）
└── mise（环境管理）
    ├── 任务运行：just
    └── 代码
        ├── 代码格式：dprint
        └── 拼写检查：typos
```

## 结构

```text
.
├── .editorconfig     # 代码风格
├── .gitattributes    # Git 属性
├── .gitignore        # Git 忽略
├── .typos.toml       # 拼写检查
├── dprint.jsonc      # 代码格式
├── justfile          # 任务运行
├── mise.lock         # 工具版本
├── mise.toml         # 开发环境
└── README.md         # 项目说明
```
