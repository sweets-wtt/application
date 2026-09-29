# application

## 概览

- 用途: 框架
- 状态: 工具链

## 架构

```text
根: application
├── 环境管理: mise
│   ├── 代码格式: dprint
│   ├── 拼写检查: typos
│   ├── 提交检查: cocogitto
│   ├── 钩子管理: lefthook → cocogitto
│   ├── 语法检查: actionlint → github
│   ├── 工作流审计: zizmor → github
│   └── 密钥扫描: gitleaks
├── GitHub: github
└── 依赖更新: renovate → mise
```

## 结构

```text
.
├── .github            # GitHub
│   └── workflows      # 工作流
│       └── ci.yaml    # 持续集成
├── .editorconfig      # 代码风格
├── .gitattributes     # Git 属性
├── .gitignore         # Git 忽略
├── .gitleaks.toml     # 密钥扫描
├── .typos.toml        # 拼写检查
├── dprint.jsonc       # 代码格式
├── lefthook.yaml      # 钩子管理
├── mise.lock          # 工具版本
├── mise.toml          # 环境管理
├── renovate.jsonc     # 依赖更新
└── README.md          # 项目说明
```
