# application

## 概览

- 状态: 服务

## 架构

```text
根: application
├── 环境管理: mise
├── 配置校验: config-file-validator
├── 代码格式: dprint
├── 拼写检查: typos
├── 提交检查: cocogitto
├── 钩子管理: lefthook → cocogitto
├── 密钥检查: gitleaks
├── 漏洞扫描: trivy
├── 兼容性检查: oasdiff
├── HTTP 契约: vacuum
├── 服务编排: docker
└── HTTP 测试: hurl → docker
```

## 结构

```text
.
├── contracts             # 契约
│  └── http               # HTTP
│     ├── paths           # 路径定义
│     ├── schemas         # 模型定义
│     ├── openapi.yaml    # OpenAPI
│     └── vacuum.yaml     # 规则集
├── infra                 # 服务编排
│  ├── .env.example       # 环境变量
│  └── compose.yaml       # 容器编排
├── .dockerignore         # 构建排除
├── .editorconfig         # 代码风格
├── .gitattributes        # Git 属性
├── .gitignore            # Git 忽略
├── .gitleaks.toml        # 密钥检查
├── .typos.toml           # 拼写检查
├── docker-bake.hcl       # 镜像构建
├── dprint.jsonc          # 代码格式
├── lefthook.yaml         # 钩子管理
├── mise.lock             # 工具锁
├── mise.toml             # 环境管理
└── README.md             # 项目说明
```
