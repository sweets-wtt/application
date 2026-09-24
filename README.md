# application

## 概览

- 用途：框架
- 状态：工具链

## 架构

```text
application（根项目）
└── mise（环境管理）
    ├── 任务运行：just
    ├── 代码
    │   ├── 代码格式：dprint
    │   └── 拼写检查：typos
    ├── 提交
    │   ├── 提交检查：cocogitto
    │   └── 钩子管理：lefthook → cocogitto
    └── 安全
        ├── 密钥扫描：gitleaks
        └── 漏洞扫描：trivy
```

## 结构

```text
.
├── .editorconfig     # 代码风格
├── .gitattributes    # Git 属性
├── .gitignore        # Git 忽略
├── .gitleaks.toml    # 密钥扫描
├── .typos.toml       # 拼写检查
├── cog.toml          # 提交检查
├── dprint.jsonc      # 代码格式
├── justfile          # 任务运行
├── lefthook.yaml     # 钩子管理
├── mise.lock         # 工具版本
├── mise.toml         # 开发环境
└── README.md         # 项目说明
```
