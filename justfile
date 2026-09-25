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
    # Python 依赖
    uv sync --locked --all-packages
    # Typescript 依赖
    bun install --frozen-lockfile

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
    # 工作区检查
    just lint-workspace

# 格式化
format:
    # 格式化代码
    dprint fmt
    # 工作区格式化
    just format-workspace

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
    # 执行测试
    hurl --test --retry 15 --retry-interval 2000 --variables-file infra/.env tests/

# 观测
observe:
    # 观测验收
    hurl --test --retry 15 --retry-interval 2000 --variables-file infra/.env tests/docker/observe.hurl

# 工作区检查
lint-workspace:
    # 格式校验
    uv run ruff format --check .
    # 静态检查
    uv run ruff check .
    # 类型检查
    uv run ty check .
    # TS 格式校验
    bunx oxfmt --check --no-error-on-unmatched-pattern '**/*.{ts,tsx,mts,cts,js,jsx,mjs,cjs}'
    # TS 代码检查
    bunx oxlint --no-error-on-unmatched-pattern

# 工作区格式化
format-workspace:
    # 格式化代码
    uv run ruff format .
    # TS 格式化
    bunx oxfmt --no-error-on-unmatched-pattern '**/*.{ts,tsx,mts,cts,js,jsx,mjs,cjs}'

# 测试
test:
    # 运行测试
    uv run --locked --all-packages pytest

# 迁移
migrate:
    # 执行迁移
    uv run alembic upgrade head
