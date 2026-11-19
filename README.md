# application

## 技术架构

```text
根: application
└── 环境管理: mise
    ├── 任务管理: task
    ├── 配置格式: dprint
    ├── 拼写检查: typos
    ├── 提交规范: cocogitto
    ├── 钩子管理: lefthook
    ├── 密钥扫描: gitleaks
    ├── 漏洞扫描: trivy
    ├── 工作流检查: actionlint
    └── 工作流审计: zizmor
```

## 项目结构

```text
.
├── .github/          # CI 配置
├── .editorconfig     # 代码风格
├── .gitattributes    # 版本属性
├── .gitignore        # 版本忽略
├── .gitleaks.toml    # 密钥扫描
├── .trivyignore      # 漏洞忽略
├── cog.toml          # 提交规范
├── dprint.jsonc      # 配置格式
├── lefthook.yaml     # 钩子管理
├── mise.lock         # 工具版本
├── mise.toml         # 环境管理
├── trivy.yaml        # 漏洞扫描
├── typos.toml        # 拼写检查
├── README.md         # 项目说明
└── Taskfile.yaml     # 任务管理
```
