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
    mise -->|执行环境| typos["typos（拼写检查）"]
    mise -->|执行环境| cocogitto["cocogitto（提交检查）"]
    mise -->|执行环境| lefthook["lefthook（钩子管理）"]
    lefthook -->|调用| cocogitto["cocogitto（提交检查）"]
    mise -->|执行环境| gitleaks["gitleaks（密钥扫描）"]
    just -->|调用| gitleaks["gitleaks（密钥扫描）"]
    application -->|依赖| renovate["renovate（依赖更新）"]
    renovate -->|版本更新| mise["mise（环境管理）"]
    mise -->|执行环境| sops["sops（密钥加密）"]
    sops -->|依赖| age["age（加密工具）"]
```

## 结构

```text
.
├── .editorconfig     # 代码风格
├── .gitattributes    # Git 属性
├── .gitignore        # Git 忽略
├── .gitleaks.toml    # 密钥扫描
├── .sops.yaml        # 密钥加密
├── .typos.toml       # 拼写检查
├── cog.toml          # 提交检查
├── justfile          # 任务运行
├── lefthook.yaml     # 钩子管理
├── mise.lock         # 工具版本
├── mise.toml         # 开发环境
├── renovate.json5    # 依赖更新
└── README.md         # 项目说明
```
