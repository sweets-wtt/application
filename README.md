# application

## 架构

```text
根: application
└── 环境管理: mise
    ├── 任务运行: task
    ├── 配置校验: config-file-validator
    ├── 配置格式: dprint
    ├── 拼写检查: typos
    ├── 提交检查: cocogitto
    ├── 钩子管理: lefthook
    └── 安全扫描: trivy
```

## 结构

```text
.
├── .cfv.toml            # 校验配置
├── .editorconfig        # 代码风格
├── .gitattributes       # Git 属性
├── .gitignore           # Git 忽略
├── .typos.toml          # 拼写检查
├── dprint.jsonc         # 配置格式
├── lefthook.yaml        # 钩子管理
├── mise.lock            # 工具锁定
├── mise.toml            # 环境管理
├── trivy-secret.yaml    # 密钥规则
├── trivy.yaml           # 安全扫描
├── README.md            # 项目说明
└── Taskfile.yaml        # 任务定义
```
