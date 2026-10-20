# application

## 架构

```text
根: application
└── 环境管理: mise
    ├── 任务运行: task
    ├── 配置校验: config-file-validator
    ├── 配置格式: dprint
    └── 拼写检查: typos
```

## 结构

```text
.
├── .cfv.toml         # 校验配置
├── .editorconfig     # 代码风格
├── .gitattributes    # Git 属性
├── .gitignore        # Git 忽略
├── .typos.toml       # 拼写检查
├── dprint.jsonc      # 配置格式
├── mise.lock         # 工具锁定
├── mise.toml         # 环境管理
├── README.md         # 项目说明
└── Taskfile.yaml     # 任务定义
```
