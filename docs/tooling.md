# 工程门禁与工具链

## 1. 工具版本（mise.toml）

全部通过 aqua 固定版本，`auto_install = false`、`locked = true`、`lockfile = true`、`not_found_system_fallback =
false`。

| 工具       | 版本    | 用途               |
| ---------- | ------- | ------------------ |
| trivy      | 0.76.2  | 镜像漏洞扫描       |
| uv         | 0.13.7  | Python 包管理      |
| cocogitto  | 7.0.0   | 提交规范与版本发布 |
| typos      | 1.52.2  | 拼写检查           |
| vacuum     | 0.40.0  | OpenAPI 校验与打包 |
| dprint     | 0.64.3  | 多语言格式化       |
| lefthook   | 2.2.2   | Git 钩子           |
| gitleaks   | 8.30.1  | 密钥扫描           |
| task       | 3.54.0  | 任务编排           |
| actionlint | 1.7.12  | 工作流语法检查     |
| zizmor     | 1.32.0  | 工作流安全审计     |
| bun        | 1.4.4   | JS 运行时          |
| oasdiff    | v1.37.0 | 契约兼容性检查     |

## 2. Taskfile 任务图

### 2.1 变量

```yaml
UV: "uv run --locked"
COMPOSE: "docker compose -f infra/compose.yaml -p application"
SPEC: contracts/http/dist/openapi.yaml
PYTHON_MODELS: apps/server/src/server/generated/contracts.py
GENERATED: "<PYTHON_MODELS> apps/web/src/api/generated/http apps/web/src/api/generated/schemas contracts/http/dist"
REGISTRY: "" # 默认空
TAG: "latest"
```

### 2.2 主要任务

| 任务                                                     | 说明                                                                                                                                         |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `install`                                                | 聚合 install-tools / install-python / install-typescript                                                                                     |
| `check`                                                  | 聚合 check-format / check-taskfile / check-spell / check-secret / check-github / check-compose / check-python / check-typescript / check-api |
| `format`                                                 | 全仓格式化                                                                                                                                   |
| `build` / `build-web`                                    | 构建                                                                                                                                         |
| `build-image` / `build-image-server` / `build-image-web` | 构建镜像                                                                                                                                     |
| `check-size`                                             | 前端体积预算                                                                                                                                 |
| `test` / `test-python` / `test-typescript` / `test-e2e`  | 测试                                                                                                                                         |
| `bundle-spec`                                            | 打包契约到 dist                                                                                                                              |
| `codegen` / `codegen-python` / `codegen-typescript`      | 生成双端产物                                                                                                                                 |
| `check-codegen`                                          | 生成后 `git diff --exit-code`                                                                                                                |
| `scan-vuln`                                              | trivy 扫描                                                                                                                                   |
| `ci`                                                     | `check` + `scan-vuln`                                                                                                                        |
| `install-hooks`                                          | 安装 lefthook                                                                                                                                |
| `check-commit`                                           | cocogitto 校验提交信息                                                                                                                       |
| `compose-up` / `compose-down`                            | 本地编排                                                                                                                                     |

### 2.3 两个值得注意的编排问题

* **`check` 不含 `check-codegen`**：漂移检查只在 pre-push 钩子与 CI 的 test job 里跑，本地 `task check`
  通过不代表生成物同步。
* **`check-typescript` 依赖 `build-types`**，而 `build-types` 跑的是完整 `bun run build`——只为生成 `components.d.ts`
  却付出全量构建代价。

## 3. CI 流水线

### 3.1 ci.yaml（184 行）

触发：`pull_request` + `push(main)`。权限 `contents: read`。并发组
`${{github.workflow}}-${{github.ref}}`，`cancel-in-progress: true`。

| job           | 超时 | 内容                                                                                                                                        |
| ------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `lint`        | 15   | setup（fetch-depth 0，不写 env-file）→ `task ci`                                                                                            |
| `test`        | 20   | setup（默认）→ `task test` + `task check-size` + `task check-codegen`                                                                       |
| `e2e`         | 20   | setup（dependencies: bun，不写 env-file）→ 安装 chromium → `task test-e2e`                                                                  |
| `images`      | 20   | setup（container-runtime: true）→ `task build-image`                                                                                        |
| `compat`      | 10   | **仅 PR**，`oasdiff breaking --fail-on ERR "origin/main:contracts/http/dist/openapi.yaml" contracts/http/dist/openapi.yaml`，基线缺失则跳过 |
| `commit-lint` | 5    | **仅 PR**，对 `git rev-list --no-merges "$BASE"..HEAD` 逐个 `cog verify`                                                                    |
| `deps-review` | —    | **仅 PR**，`actions/dependency-review-action` v5.0.0                                                                                        |

### 3.2 release.yaml（91 行）

仅 `workflow_dispatch`。权限 `contents: write` + `packages: write`。并发组 `release`，`cancel-in-progress: false`。

流程：checkout（fetch-depth 0，`persist-credentials: false`）→ mise-action（version `2026.8.14`）→ `docker version` →
配置 bot 身份 → `cog bump --auto` → `git describe --tags --abbrev=0` 取 tag → `git push main --tags` → `docker login
ghcr.io` → `task build-image` → 推送 `server:${TAG}` 与 `web:${TAG}`。

`REGISTRY` 为 `ghcr.io/${{github.repository_owner}}/`。

### 3.3 复合 action（.github/actions/setup/action.yaml，73 行）

| input               | 默认值    | 作用                                                                           |
| ------------------- | --------- | ------------------------------------------------------------------------------ |
| `fetch-depth`       | `"1"`     | checkout 深度                                                                  |
| `dependencies`      | `all`     | `all` / `bun` / `none`                                                         |
| `env-file`          | `"true"`  | 用 `sed 's/=$/=placeholder/' infra/.env.example > infra/.env` 生成占位环境文件 |
| `container-runtime` | `"false"` | 是否执行 `docker version`                                                      |

步骤：checkout（`persist-credentials: false`）→ mise-action → 若 `all` 则 `task install` → 若 `container-runtime` 则
`docker version` → 若 `bun` 则 `bun install --frozen-lockfile` → 若 `env-file` 则生成 `infra/.env`。

## 4. Git 钩子（lefthook.yaml）

`min_version: "2.2.2"`、`assert_lefthook_installed: true`、`no_tty: true`。模板 `task = "mise exec -- task"`。

| 钩子         | 命令                               |
| ------------ | ---------------------------------- |
| `pre-commit` | `task check`                       |
| `commit-msg` | `task check-commit -- --file {1}`  |
| `pre-push`   | `task check-codegen` + `task test` |
| `post-merge` | `task install`                     |

## 5. 各工具配置要点

### 5.1 ruff.toml（74 行）

* `target-version = "py314"`、`line-length = 100`、`extend-exclude = ["**/generated/**"]`
* `select = ["ALL", "DOC201", "RUF029"]`，`ignore = ["COM812", "CPY001", "D415", "ISC001", "RUF002", "RUF003"]`
* `preview = true`、`explicit-preview-rules = true`
* isort：`force-single-line`、`force-sort-within-sections`、`known-first-party = ["server"]`、`lines-after-imports = 2`
* `flake8-import-conventions.banned-from = ["typing"]` → 全仓写 `import typing` 而非 `from typing import ...`
* `banned-api`：`datetime.datetime.utcnow` → 「使用 `datetime.now(UTC)`」；`requests` → 「使用 httpx」
* `bugbear.extend-immutable-calls` 含 `fastapi.Body/Cookie/Depends/File/Form/Header/Path/Query/Security`
* `pydocstyle.convention = "google"`
* per-file-ignores：`apps/*/src/*/api/**` 忽略 `ARG001`；`apps/*/tests/**` 忽略 `S101`
* `format.docstring-code-format = true`、`line-ending = "lf"`

### 5.2 ty.toml（35 行）

* `src.exclude = ["**/generated"]`
* `environment.python-version = "3.14"`、`python-platform = "linux"`
* `analysis.return-type-inference = "always"`、`strict-equality-semantics = true`、`strict-generic-narrowing = true`
* `rules.all = "error"`
* overrides：`apps/server/tests/**` 忽略 `possibly-missing-attribute`

### 5.3 .oxlintrc.jsonc（117 行）

* plugins：eslint / import / jsdoc / node / oxc / promise / typescript / unicorn / vitest / vue
* categories：correctness / nursery / pedantic / perf / restriction / style / suspicious **全 error**
* `options.reportUnusedDisableDirectives = "error"`、`typeAware = true`、`typeCheck = true`
* 关键规则：`eslint/id-length`（max 40 / min 2）、`no-duplicate-imports`（allowSeparateTypeImports）、`one-var:
  never`、`require-unicode-regexp`、`import/no-unassigned-import`（allow
  `**/*.css`、`virtual:*`）、`oxc/no-barrel-file`（threshold
  300）、`typescript/return-await`（error-handling-correctness-only）、`unicorn/filename-case`（camel/kebab/pascal）、`vitest/consistent-test-filename`、`vitest/prefer-expect-assertions`（onlyFunctionsWithAsyncKeyword）
* `ignorePatterns`：`**/generated/**`、`**/components.d.ts`
* overrides：测试文件开 `vitest/require-hook`；e2e 关 `vitest/prefer-importing-vitest-globals`；`*.vue` 与 `*.d.ts` 关
  `import/unambiguous`

### 5.4 .oxfmtrc.jsonc（36 行）

* `printWidth: 120`、`htmlWhitespaceSensitivity: "ignore"`、`objectWrap: "collapse"`、`experimentalOperatorPosition:
  "start"`
* `sortImports.groups`：builtin / external / [internal, subpath] / [parent, sibling, index] / style / type /
  unknown；`sortSideEffects: true`
* `ignorePatterns`：`**/components.d.ts`；overrides 对 `**/generated/**` 关 `sortImports`

### 5.5 dprint.jsonc（53 行）

* `lineWidth: 120`；includes `**/*.{json,jsonc,md,yaml,toml}` 与 `**/Dockerfile`；excludes `**/dist/**`
* 插件：dockerfile 0.8.0、json 0.26.0、markdown 0.29.0、toml 0.10.0、yaml 0.6.0
* `dockerfile.indentStages: true`
* json：array/object `preferSingleLine`、`trailingCommas: "never"`
* markdown：`emphasisKind: "asterisks"`、`list.unorderedMarker: "asterisks"`、`textWrap: "always"`
* toml：`preferSingleLine`；yaml：`formatComments: true`

### 5.6 cog.toml（44 行）

* `from_latest_tag: true`、`ignore_merge_commits: true`、`tag_prefix: "v"`
* changelog：owner `sweets-wtt`、path `CHANGELOG.md`、remote `github.com`、repository `application`、template `remote`
* commit_types：build / chore / ci / docs / style / test 设 `omit_from_changelog = true`；feat / fix / perf / refactor /
  revert 各有 `changelog_title`

### 5.7 其他

* **.gitleaks.toml**（15 行）：`extend.useDefault = true`；自定义规则 `pipe-to-shell`，keywords `["curl", "wget"]`，匹配
  curl/wget 管道到 sh/bash/zsh/ksh/dash
* **zizmor.yaml**（7 行）：`rules.self-repository.ignore = ["ci.yaml"]`
* **typos.toml**（19 行）：`files.extend-exclude = ["components.d.ts", "generated"]`；忽略形如 `AB123`
  的编号；`type.lock.check-file = false`
* **.editorconfig**（27 行）：`root = true`；`[*]` utf-8 / lf / space / 2 / 末尾换行 / 去尾空格；`[*.md]`
  保留尾空格；`[*.py]` 缩进 4
* **.gitattributes**（8 行）：`* text=auto eol=lf`；`**/generated/**` 与 `**/components.d.ts` 标
  `linguist-generated=true`

## 6. 忽略规则

### 6.1 .gitignore（94 行）

分节：编辑器与 OS、环境变量（`.env`、`.env.*`，例外
`!.env.example`、`!.env.*.example`）、依赖、日志、Python（`.hypothesis` / `.mypy_cache` / `.pyright` / `.pytest_cache` /
`.ruff_cache` / `pytest-of-*` / `*.egg-info`）、覆盖率、TypeScript、测试产物（`test-results/` / `playwright-report/` /
`blob-report/`）、构建产物（`dist/` 但例外
`!contracts/*/dist/`、`.task/`）、本地环境（`infra/compose.override.yaml`、`infra/secrets/*`）。

### 6.2 .dockerignore（63 行）

分节：`.git/`、`.github/`、`**/.env` 与 `**/.env.*`、`**/node_modules/`、`**/.venv/`、Python
缓存、覆盖率、`*.tsbuildinfo`、`**/dist/`、`**/.task/`、`apps/*/tests/`、`infra/` 但例外
`!infra/Caddyfile`、`contracts/`。

> `!infra/Caddyfile` 这条例外是 Web 镜像构建的硬依赖——删掉它，`COPY infra/Caddyfile` 就会失败。

## 7. 关键文件

| 文件                                                                        | 作用         |
| --------------------------------------------------------------------------- | ------------ |
| [Taskfile.yaml](../Taskfile.yaml)                                           | 任务编排     |
| [mise.toml](../mise.toml)                                                   | 工具版本     |
| [.github/workflows/ci.yaml](../.github/workflows/ci.yaml)                   | CI           |
| [.github/workflows/release.yaml](../.github/workflows/release.yaml)         | 发布         |
| [.github/actions/setup/action.yaml](../.github/actions/setup/action.yaml)   | 复合 setup   |
| [lefthook.yaml](../lefthook.yaml)                                           | Git 钩子     |
| [ruff.toml](../ruff.toml) / [ty.toml](../ty.toml)                           | Python 质量  |
| [.oxlintrc.jsonc](../.oxlintrc.jsonc) / [.oxfmtrc.jsonc](../.oxfmtrc.jsonc) | TS 质量      |
| [dprint.jsonc](../dprint.jsonc)                                             | 多语言格式化 |
