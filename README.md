# application

## 概览

- 用途：框架
- 状态：契约

## 架构

```text
application（根）
├── mise（环境管理）
│   ├── 代码格式：dprint
│   ├── 拼写检查：typos
│   ├── 提交检查：cocogitto
│   └── 钩子管理：lefthook → cocogitto
└── contracts（契约）
    └── 契约检查：vacuum → openapi
```

## 结构

```text
.
├── contracts               # 契约
│   └── http                # HTTP
│       ├── openapi.yaml    # 接口规范
│       ├── vacuum.yaml     # 契约检查
│       ├── paths           # 接口定义
│       └── schemas         # 数据模式
├── .editorconfig           # 代码风格
├── .gitattributes          # Git 属性
├── .gitignore              # Git 忽略
├── .typos.toml             # 拼写检查
├── dprint.jsonc            # 代码格式
├── lefthook.yaml           # 钩子管理
├── mise.lock               # 工具版本
├── mise.toml               # 环境管理
└── README.md               # 项目说明
```
