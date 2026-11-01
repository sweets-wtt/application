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

# 生成 Python 契约
codegen-py:
    # 同步开发依赖 - 含 codegen 工具
    uv sync --locked --all-packages
    # 在 Python 契约包内生成模型 - 显式输入路径、关闭时间戳、输出路径级响应模型
    cd packages/python/contracts; uv run datamodel-codegen --input ../../../contracts/http/openapi.yaml --disable-timestamp --openapi-scopes paths --strict-types int

# 生成 TypeScript 契约
codegen-ts:
    # 在 TypeScript 契约包内生成客户端
    cd packages/typescript/contracts; bun x orval
    # 统一生成物格式
    bun x oxfmt packages/typescript/contracts/src/http packages/typescript/contracts/src/schemas

# 生成契约代码
codegen: codegen-py codegen-ts

# 检查契约生成物
codegen-check: codegen
    # 生成物无差异
    git diff --exit-code -- packages/python/contracts/src/app/contracts/generated packages/typescript/contracts/src/http packages/typescript/contracts/src/schemas

# 校验
check:
    # 校验编排
    {{ compose }} config --quiet

# 构建镜像
build:
    # 构建应用镜像
    docker buildx bake -f docker-bake.hcl apps

# 构建前端
build-web:
    # 构建前端产物
    bun run --filter @app/web build

# 启动
up:
    # 启动服务
    {{ compose }} up -d --remove-orphans --wait

# 停止
down:
    # 停止服务
    {{ compose }} down --remove-orphans

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
    # TS 类型检查
    bunx tsc -b --noEmit
    # 应用类型检查
    bun run --filter @app/web typecheck

# 工作区格式化
format-workspace:
    # 格式化代码
    uv run ruff format .
    # TS 格式化
    bunx oxfmt --no-error-on-unmatched-pattern '**/*.{ts,tsx,mts,cts,js,jsx,mjs,cjs}'

# 测试
test:
    # 后端测试
    uv run --locked --all-packages pytest
    # 前端测试
    bun run --filter @app/web test

# 迁移
migrate:
    # 执行迁移
    uv run alembic -c apps/server/alembic.ini upgrade head
