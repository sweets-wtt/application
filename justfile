# justfile - `https://github.com/casey/just`

# 不稳定特性
set unstable

# shell
set shell := ["bash", "-cu"]

# Windows shell
set windows-shell := ["powershell", "-NoProfile", "-Command"]

# Compose 参数
compose := "docker compose -f infra/compose.yaml --project-directory infra"

# 默认
default:
    # 列出任务
    @just --list

# 初始化
setup:
    # 安装工具
    mise install --locked

# 检查
lint:
    # 检查格式
    dprint check
    # 拼写检查
    typos
    # 密钥扫描
    gitleaks git --config .gitleaks.toml .
    # 工作流语法
    actionlint
    # 工作流审计
    zizmor .github/workflows
    # 编排校验
    just check

# 格式化
format:
    # 格式化代码
    dprint fmt

# 钩子
hooks:
    # 安装钩子
    lefthook install

# 审计
audit:
    # 依赖漏洞
    trivy fs --scanners vuln --severity HIGH,CRITICAL --exit-code 1 .
    # 配置漏洞
    trivy fs --scanners misconfig --severity HIGH,CRITICAL --exit-code 1 .

# 集成
ci:
    # 代码检查
    just lint
    # 安全扫描
    just audit

# 契约
contracts:
    # 校验契约
    vacuum lint --ruleset contracts/http/vacuum.yaml contracts/http/openapi.yaml

# 校验
check:
    # 校验编排
    {{ compose }} config --quiet

# 启动
up:
    # 启动服务
    {{ compose }} --profile check up -d --remove-orphans --wait

# 停止
down:
    # 停止服务
    {{ compose }} down --remove-orphans

# 测试
verify:
    # 启动服务
    just up
