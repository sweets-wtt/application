# 问题清单与改进建议

按严重度排序。每条都给出具体文件与行号，便于直接定位。

## 高

### 1. e2e 缺 `baseURL`，`page.goto("/")` 会抛 `Invalid URL`

`apps/web/playwright.config.ts` 的 `use` 只有 `{ screenshot, trace, video }`，**没有 `baseURL`**；而
`apps/web/tests/e2e/smoke.spec.ts:7` 用的是相对路径 `await page.goto("/")`。

Playwright 只有在配置了 `baseURL` 时才会把相对路径拼成绝对 URL，否则 `page.goto("/")` 会抛 `Invalid
URL`。`webServer`（`playwright.config.ts:9`）只负责起服务，**不会**自动推导 `baseURL`。Taskfile 的
`test-e2e`（`Taskfile.yaml:231-237`）也只做 `build-web` + `bunx playwright test`，没有注入 `PLAYWRIGHT_TEST_BASE_URL`
之类的环境变量。

**修法**：`use: { baseURL: "http://127.0.0.1:4173", ... }`。

### 2. 生产环境未切 JSON 日志

`apps/server/src/server/core/logging.py:84` 的渲染器由 `APP_LOG_FORMAT` 决定，默认
`console`（`core/config.py:16`）。但生产链路上**没有任何地方设置该变量**：

* `apps/server/Dockerfile` 只设了 `PATH` 和 `GRANIAN_WORKERS`
* `infra/compose.yaml` 的 `api` 服务**完全没有 `environment:` 块**
* `infra/.env.example` 也没有这个变量

而 `infra/compose.yaml:8-10` 明确把日志驱动设为 `journald`。结果是：structlog 精心配置的 `JSONRenderer`
分支在生产从未启用，journald 里存的是带 ANSI 颜色码的 `ConsoleRenderer` 输出，无法被日志系统按字段检索。这与引入
structlog 的初衷（结构化日志）直接矛盾。

**修法**：Dockerfile 加 `ENV APP_LOG_FORMAT=json`，或 compose 的 `api` 服务补 `environment: { APP_LOG_FORMAT: "json"
}`。

### 3. 统一错误结构在 500 场景失效

`apps/server/src/server/main.py:18` 只注册了一个异常处理器：

```python
app.add_exception_handler(AppError, handle_app_error)
```

Starlette 按异常类 MRO 匹配处理器，因此只有 `AppError` 及其子类会进入 `handle_app_error`。`core/exceptions.py:41-43` 的
fallback 分支：

```python
fallback = AppError()
return JSONResponse(status_code=fallback.status_code, content={"detail": fallback.detail})
```

在真实请求路径上**永远走不到**——未捕获的 `ValueError` 会冒泡到 Starlette 的 `ServerErrorMiddleware`，返回 `text/plain`
的 `Internal Server Error`，而不是 `{"detail": "内部错误"}`。于是「统一错误结构」的承诺在 500
场景下失效，客户端拿到的是非 JSON。

更微妙的是 `apps/server/tests/core/test_exceptions.py:79-84` 恰好测的就是这条不可达路径，测试通过但给出虚假安全感。

**修法**：要么注册 `Exception` 兜底处理器，要么删掉 fallback 分支并把签名收窄为 `exc: AppError`，让类型与运行时一致。

### 4. 持久化层与 store 形状不一致，`save → load` 不幂等

`apps/web/src/stores/app.ts:16` 的 store state 是**空对象**：

```ts
const useAppStore = defineStore("app", () => ({}), { persist: { ... } });
```

而 `apps/web/src/lib/storage.ts:22` 的 `stateSchema` 要求 `{ locale, version }`，`defaultState`（`storage.ts:28`）也是
`{ locale: "zh-CN", version: "1" }`。

后果链条：

1. 首次运行 `localStorage["app"]` 不存在 → `parseState(undefined)` → `defaultState` → pinia 把 `{locale, version}`
   **合并进一个声明为 `{}` 的 store**，运行时多出两个类型上不存在的字段
2. 序列化时 `serializeState({})` → `"{}"`
3. 下次读取 `parseState("{}")` → `migrate({})` → `version = "0"` → `migrations["0"]` 不存在（`storage.ts:31`
   是**空表**）→ `settle({}, "0")` → `undefined` → 回退 `defaultState`

即 **`save → load` 不幂等**：写进去的 `{}` 读出来变成 `{locale, version}`。同时 `migrations` 表为空意味着 `migrate`
永远无法升级任何版本，`MAX_MIGRATION_STEPS = 16`（`storage.ts:13`）的防环逻辑目前无对象可防。

**修法**：要么把 `locale` 真正放进 store 的 setup 返回值，要么把 `storage.ts` 的 schema 与 store 对齐。

### 5. 没有 `vue-tsc`，SFC 类型实际未被检查

* `apps/web/package.json` 的 devDependencies **没有 `vue-tsc`**，也没有 `tsc --noEmit` 脚本
* `apps/web/tsconfig.json:68` 的 `include` 只有 `["src", "tests", "components.d.ts"]`，**不含** `vite.config.ts` /
  `orval.config.ts` / `playwright.config.ts` / `uno.config.ts`
* `apps/web/src/env.d.ts:4-8` 用宽泛的 `*.vue` 模块声明兜底

三者叠加的结果：`<script setup>` 里的类型错误、模板里的 props 不匹配，**都不会被任何工具报出来**。实际类型检查只靠
oxlint 的 `typeAware: true` + `typeCheck: true`，而 oxlint 对 `.vue` 的类型感知能力有限。

**修法**：加 `vue-tsc --noEmit` 并把配置文件纳入 `include`。

## 中

### 6. 配置双源，且 `.env` 实际不生效

`apps/server/src/server/core/config.py:20` 定义了单例 `settings`，但 `core/logging.py` **完全绕过它**，直接读环境变量：

```python
name = os.environ.get("APP_LOG_LEVEL", "").upper()
json_mode = os.environ.get("APP_LOG_FORMAT") == "json"
```

`core/bootstrap.py:12-13` 的 `setdefault` 因此是**冗余回路**：

* 若环境变量已设置 → `setdefault` 是 no-op，`settings.log_level` 与 env 本来就相等
* 若未设置 → `setdefault` 写入 `"INFO"`/`"console"`，而 `_level()` 在缺失时本来也回退 `logging.INFO`、`json_mode`
  本来也是 `False`

即这段代码在任何情况下都不改变行为，却制造了「配置有两个真相源」的认知负担。

同时 `config.py:10` 的 `model_config = {"env_prefix": "APP_"}` **没有 `env_file`**，pydantic-settings 不会读 `.env`
文件；而 `apps/server/README.md:112` 写的是「本地 `.env` 不提交；生产通过容器环境变量或密钥管理注入」，暗示本地存在
`.env` 工作流。实际本地放 `.env` 不会生效，只能靠 shell 导出。

**修法**：`logging.py` 改为 `from server.core.config import settings` 后读字段，删掉 `bootstrap.py:12-13`；`config.py`
补 `SettingsConfigDict(env_prefix="APP_", env_file=".env")`。

### 7. 脱敏只做一层，且安全相关逻辑零测试

`apps/server/src/server/core/logging.py:60-65` 的 `redact` 只遍历 `event_dict` 的**顶层**键：

```python
for key, value in event_dict.items():
    if str(key).lower() in SENSITIVE_KEYS:
        event_dict[key] = "***"
    elif isinstance(value, str):
        event_dict[key] = _mask(value)
return event_dict
```

`elif isinstance(value, str)` 意味着嵌套结构被整体跳过。以下调用会**完整泄漏**：

```python
logger.info("login", user={"password": "hunter2"})  # dict 值不递归
logger.info("batch", items=[{"token": "abc"}])  # list 值不递归
logger.info("cfg", payload=b'{"password": "x"}')  # bytes 不是 str
```

`SENSITIVE_KEYS` 只含 5 个键名，`api-key`、`access_token`、`refresh_token`、`private_key`、`session`
等常见变体不在其中；`_mask` 的正则也只覆盖 Bearer / AKIA / 键值对三种形态，无法识别 JWT、GitHub `ghp_`、Slack `xoxb-`
等。

而 `apps/server/tests/` 下**没有任何 logging 测试**——全仓最长的模块（149 行）、唯一涉及安全语义的模块，断言数为 0。

附带一个小问题：`logging.py:135` 直接覆盖根 handler（`root.handlers = [handler]`），会丢弃 import 之前已存在的任何根
handler，属于侵入式全局状态修改。

**修法**：`redact` 改为递归遍历 dict/list/tuple；`SENSITIVE_KEYS` 扩充并支持前缀/后缀匹配；补
`tests/core/test_logging.py` 覆盖 `_mask` 三种模式、`redact` 的顶层键命中、嵌套结构、非 str 值四类场景。

### 8. `schemathesis` 进了生产镜像，且配置依赖 cwd

`apps/server/pyproject.toml` 把契约测试工具放进了 `dependencies`：

```toml
dependencies = [
  "fastapi>=0.141.1",
  "granian>=2.8.2",
  "pydantic-settings>=2.15.0",
  "pydantic>=2.13.5",
  "schemathesis>=4.26.1", # ← 测试工具
  "structlog>=25.4.0",
]
```

`apps/server/Dockerfile:18` 的 `--no-dev` 只能剔除 `[dependency-groups].dev`，剔不掉 `dependencies`，因此 schemathesis
及其传递依赖（hypothesis、jsonschema、requests 等）会**全部进入生产镜像**。`apps/server/README.md:15`
自己也把它归在「契约测试」而非运行时能力。

第二个问题：`apps/server/schemathesis.toml` 的生效依赖 cwd。`SchemathesisConfig.discover()` 从 `os.getcwd()` 向上找，遇
`.git` 停止。`Taskfile.yaml:220-224` 用 `dir: apps/server` 才命中；若开发者按直觉在仓库根跑 `pytest
apps/server`，`seed = 42` 与 `deterministic = true` 会**静默失效**，测试变成非确定性，且没有任何报错提示。

配套的脆弱点：`apps/server/tests/features/health/test_router.py:13` 用 `parents[5]`
硬算仓库根，测试文件一旦移动层级就会静默指向错误位置。

**修法**：`schemathesis` 移到 `[dependency-groups].dev`；配置发现改为在 `conftest.py` 里显式加载；`_SCHEMA_PATH` 改用
`importlib.resources` 或从 `pyproject.toml` 所在目录向上查找。

### 9. 开发环境没有代理

`apps/web/src/config/env.ts:2` 默认 `""`（同源相对路径），`apps/web/vite.config.ts` **完全没有 `server.proxy`
配置**。于是 `bun run dev` 时 `fetch("/healthz")` 打到 Vite dev server 自身 → 404 → 首页永远显示「服务端离线」。

而 `apps/web/README.md:179` 明确写着：

> 本地开发可设置绝对 API 地址，或在 Vite 中配置 `/healthz`、`/api` 代理，保持与生产同源

**文档承诺的代理配置并不存在**。要么补 `server.proxy`，要么在 README 里删掉这半句。

### 10. 错误处理信息量不足，且没有 404 兜底

`apps/web/src/api/client.ts:119-121`：

```ts
if (!response.ok) {
  throw new Error(`${response.status} ${path}`);
}
```

* **丢弃响应体**：后端统一信封里的 `message` 拿不到，前端无法区分「业务错误码」和「网络错误」，也无法做 i18n 提示
* **无超时**：未使用 `AbortSignal.timeout`，请求可能永久挂起（`useHealthCheck` 的 `retry: 1` 也救不了）
* **无全局兜底**：`main.ts` 没有 `app.config.errorHandler`，`router/routes.ts` 没有 catch-all 路由 →
  未知路径渲染空白页，未捕获异常只进 console

### 11. 文档漂移（三处）

* `infra/secrets/README.md` 提到 `task secrets-init`、`task secrets-edit`、根目录 `.sops.yaml`、以及 compose 的 `api`
  服务通过 `env_file` 加载 `secrets/app.env` —— **全部不存在**（Taskfile 无 secrets 任务、无 `.sops.yaml`、compose 无
  `env_file`）。且该目录被 `.gitignore:94` 的 `infra/secrets/*` 忽略，未 tracked
* `apps/web/README.md:145` 说「修改 `contracts/http/openapi.yaml` 后重新生成」，但 orval 实际读的是
  `contracts/http/dist/openapi.yaml`，中间隔着 `bundle-spec` 这一步
* `apps/web/README.md:179` 承诺的 Vite 代理（见问题 9）

## 低

### 12. 基础镜像未固定

`apps/server/Dockerfile` 用 `python:3.14-slim` 与 `ghcr.io/astral-sh/uv:latest`，`apps/web/Dockerfile` 用
`oven/bun:1`——都是浮动 tag。只有 Caddy 按 digest
固定（`caddy:2.11.9@sha256:e40b94d0...`），说明作者知道该怎么做，只是没做完。

### 13. 旧工作区残留

`apps/web/node_modules/@app` 下有 6 个指向已不存在路径的 Junction：

| 名称        | 指向                            |
| ----------- | ------------------------------- |
| `auth`      | `packages/typescript/auth`      |
| `contracts` | `packages/typescript/contracts` |
| `log`       | `packages/typescript/log`       |
| `realtime`  | `packages/typescript/realtime`  |
| `session`   | `packages/typescript/session`   |
| `state`     | `packages/typescript/state`     |

即旧的多包工作区（`packages/typescript/*`）残留，`git status` 会报 "could not open directory
'apps/web/node_modules/@app/...'" 警告。

### 14. `check` 不含 `check-codegen`

漂移检查只在 pre-push 钩子与 CI 的 test job 里跑，本地 `task check` 通过不代表生成物同步。

### 15. `check-typescript` 触发整包构建

它依赖 `build-types`，而 `build-types` 跑完整 `bun run build`——只为生成 `components.d.ts` 却付出全量构建代价。

### 16. 双层空壳

`apps/web/src/App.vue` 与 `apps/web/src/layouts/DefaultLayout.vue` 内容完全一致（都只有 `<RouterView
/>`），多一层无意义嵌套。

### 17. `meta.title` 是死元数据

`apps/web/src/router/routes.ts:19` 定义了 `title: "首页"`，但没有任何 `afterEach` 去写 `document.title`，`index.html` 的
`<title>应用</title>` 永远不变。

### 18. `CHANGELOG.md` 不存在

`cog.toml` 声明了 `path = "CHANGELOG.md"` 但尚未生成。

## 改进优先级建议

1. **修 e2e 的 `baseURL`** —— 一行配置，让 CI 的 e2e job 真正有意义
2. **生产开 JSON 日志** —— Dockerfile 加 `ENV APP_LOG_FORMAT=json`，或 compose 补 `environment`
3. **补 `vue-tsc --noEmit`** —— 否则 SFC 的类型安全是纸面上的
4. **对齐 store 与 storage 的形状** —— 要么把 `locale` 真正放进 store，要么删掉这套迁移框架
5. **`logging.py` 改读 `settings`** —— 顺手解决配置双源，再补 `tests/core/test_logging.py`
6. **`schemathesis` 移到 dev 组** —— 生产镜像能瘦一圈
7. **清理文档漂移** —— secrets 那套、Vite 代理、契约路径三处

## 整体评价

门禁严格到近乎苛刻（`ruff select = ["ALL"]`、`ty rules.all = "error"`、oxlint 六大 category 全 error、tsconfig
四个严格开关），契约驱动贯穿到底且用 `git diff` 锁死漂移，生成物三处豁免（ruff / ty /
coverage）保持一致说明是有意设计而非遗漏。

主要短板集中在**「配置与日志的运行时一致性」**和**「前端类型检查的最后一公里」**——前者根因是 `core/logging.py`
是唯一绕过 `Settings` 直接读环境的模块，而它恰好又是唯一没有测试的模块。
