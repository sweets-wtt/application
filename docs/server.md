# apps/server（FastAPI 后端）

## 1. 规模

排除 `.venv` / `.pytest_cache` / `.hypothesis` / `.coverage` 后共 21 个文件：

| 类别 | 文件                                                                                    | 行数              |
| ---- | --------------------------------------------------------------------------------------- | ----------------- |
| 源码 | `src/server/main.py`                                                                    | 21                |
|      | `src/server/api/router.py`                                                              | 11                |
|      | `src/server/api/deps.py`                                                                | 1（仅 docstring） |
|      | `src/server/core/bootstrap.py`                                                          | 16                |
|      | `src/server/core/config.py`                                                             | 20                |
|      | `src/server/core/exceptions.py`                                                         | 43                |
|      | `src/server/core/logging.py`                                                            | 149               |
|      | `src/server/features/health/router.py`                                                  | 23                |
|      | `src/server/features/health/constants.py`                                               | 13                |
|      | `src/server/generated/contracts.py`                                                     | 33                |
|      | 6 个 `__init__.py`                                                                      | 5                 |
| 测试 | `tests/core/test_exceptions.py`                                                         | 84                |
|      | `tests/features/health/test_router.py`                                                  | 21                |
| 配置 | `pyproject.toml` / `Dockerfile` / `schemathesis.toml` / `README.md` / `.python-version` | 273               |

Python 源码约 **335 行**，测试约 **110 行**。无数据库、无 ORM、无迁移。

## 2. 目录与职责

```
apps/server/
├── src/server/
│   ├── main.py                 应用入口：装配 + 实例化 + 注册异常处理器 + 挂路由
│   ├── api/                    HTTP 层
│   │   ├── deps.py             共享依赖（当前为空占位）
│   │   └── router.py           路由聚合（api_router）
│   ├── core/                   基础设施
│   │   ├── bootstrap.py        启动装配（日志初始化）
│   │   ├── config.py           pydantic-settings 配置单例
│   │   ├── exceptions.py       AppError 体系 + 统一错误响应
│   │   └── logging.py          structlog + 标准库 logging 合流配置
│   ├── features/               业务功能（按域切分）
│   │   └── health/             健康检查
│   │       ├── constants.py    业务常量
│   │       └── router.py       存活探针
│   └── generated/              契约生成物（禁止手改）
│       └── contracts.py        datamodel-codegen 产物
├── tests/                      镜像源码结构
├── pyproject.toml / Dockerfile / schemathesis.toml / README.md / .python-version
```

分层约定写在 `apps/server/README.md:60-85`（代码放置表）与 `README.md:133-142`（代码要求）。关键约束：

* `README.md:81`：feature 内的 `router.py` 只负责 HTTP 入参与响应，复杂逻辑放 `service.py`
* `README.md:83`：契约生成物禁止手改
* `README.md:84`：不要创建全局 `services/`、`modules/`、`utils/` 目录
* `README.md:141`：禁止在 feature 之间直接导入内部实现；跨域能力放 `core/` 或共享 `schemas/`

`README.md:58` 提到的 `schemas/`（跨 feature 共享模型）目前**尚未创建**，属「按需创建」的预留位。

## 3. 启动链路

```
granian --interface asgi server.main:app
  └─ import server.main
       ├─ bootstrap()                       # 模块级副作用，import 即执行
       │    ├─ os.environ.setdefault(...)   # 回填 APP_LOG_LEVEL / APP_LOG_FORMAT
       │    └─ configure()                  # structlog + 标准库 logging 合流
       ├─ app = FastAPI(title="Server")
       ├─ app.add_exception_handler(AppError, handle_app_error)
       └─ app.include_router(api_router)
            └─ api_router.include_router(health_router)
                 └─ GET /healthz → get_health()
```

四个动作严格按序，且 `bootstrap()` 是**模块级副作用**（import 即执行）。`main.py:11` 的注释说明了原因：日志必须先于
`FastAPI()` 实例化。

没有 lifespan、没有 startup 事件、没有中间件栈（无 CORS / GZip / 请求 ID）。所以「启动链路」实际是「import 链路」。

`api_router` 本身无 prefix、无 tags、无 dependencies，`include_router(health_router)` 也未传 `prefix`，因此 feature
路由的 `path` 就是最终路径。

## 4. core 三件套

### 4.1 config.py（20 行）

| 配置项       | 环境变量         | 默认值      |
| ------------ | ---------------- | ----------- |
| `log_level`  | `APP_LOG_LEVEL`  | `"INFO"`    |
| `log_format` | `APP_LOG_FORMAT` | `"console"` |

* 前缀 `APP_`，与 `README.md:101` 的命名约定一致
* `model_config` 用的是**裸 dict** 而非 `SettingsConfigDict`，失去类型检查与 IDE 补全
* **未配置 `env_file`**，pydantic-settings 不会读 `.env`
* `settings` 在模块 import 时实例化，是全局单例，无依赖注入

### 4.2 logging.py（149 行，全仓最大模块）

两层脱敏：

* `SENSITIVE_KEYS`：`password` / `secret` / `token` / `authorization` / `api_key`
* `SENSITIVE_PATTERNS`：Bearer 令牌、AWS `AKIA` 密钥、口令键值对

正则**顺序敏感**——`logging.py:22` 的注释点明：Bearer 规则必须先于通用键值对，否则 `Authorization: Bearer xxx`
只脱掉前缀而留下令牌本体。

处理器链：合并 contextvars → 加 level → ISO8601 UTC 时间戳 → 脱敏。

**合流机制**是本文件最核心的设计：structlog 与标准库 logging 通过 `ProcessorFormatter` 汇到同一个
`StreamHandler(sys.stdout)`，`foreign_pre_chain` 让第三方库（granian / httpx）的标准库日志也走同一套脱敏 + 渲染。

渲染器由 `APP_LOG_FORMAT` 决定：JSON 模式额外挂 `format_exc_info`，console 模式交给 `ConsoleRenderer`。

### 4.3 exceptions.py（43 行）

异常体系是**类属性 + 实例覆盖**模式：子类只改 `status_code` / `detail` 两个类属性即可。`__init__` 未调用
`super().__init__()`，因此 `str(exc)` 为空串。

错误响应结构固定为 `{"detail": "<字符串>"}`，与成功响应的 `{code, message, data}` 信封**不同构**。

## 5. features/health

```python
router = APIRouter(tags=[TAG_HEALTH])


@router.get(path="/healthz", description="存活探针")
async def get_health() -> HealthzGetResponse:
    return HealthzGetResponse(code=CODE_SUCCESS, message="ok", data=Data(status=STATUS_OK))
```

* 路径 `/healthz`（无 `/api` 前缀），`async def`，无入参
* **没有显式 `response_model=`**，靠返回类型注解让 FastAPI 推断
* 返回模型全部来自 `server.generated.contracts`，路由层不自定义 schema
* 实际响应体：`{"code": 0, "message": "ok", "data": {"status": "ok"}}`
* 该端点被 `infra/compose.yaml:41-44` 的容器健康检查直接消费

`constants.py` 的三个常量全部 `UPPER_SNAKE_CASE`，其中 `STATUS_OK = Status.ok` 直接引用生成枚举，避免字符串字面量漂移。

## 6. generated/contracts.py

```python
class Status(Enum):
    ok = "ok"


class Data(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Status


class Response(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: StrictInt
    message: str
    data: dict[str, Any]


class HealthzGetResponse(Response):
    data: Data
```

生成命令（`Taskfile.yaml:274`）：

```
datamodel-codegen --input contracts/http/dist/openapi.yaml \
  --output apps/server/src/server/generated/contracts.py \
  --disable-timestamp --openapi-scopes paths --strict-types int \
  --formatters black isort
```

参数与产物一一对应：

* `--openapi-scopes paths` → 按 path operation 生成 `HealthzGetResponse`
* `--strict-types int` → `code: StrictInt`
* `--disable-timestamp` → 头部无时间戳，保证可复现
* `--formatters black isort` → 与 `ruff format` 风格兼容

`codegen-py-normalize` 再把 CRLF 统一成 LF（Windows 漂移防护）。

## 7. 工程配置

### 7.1 pyproject.toml

* 构建后端 `uv_build`，`requires-python = ">=3.14"`
* 运行时依赖：fastapi / granian / pydantic-settings / pydantic / schemathesis / structlog
* dev 组：datamodel-code-generator / pytest / pytest-asyncio / pytest-cov
* 覆盖率 `omit = ["*/generated/*"]`，与 `ruff.toml` 的 `extend-exclude`、`ty.toml` 的 `exclude`
  三处一致——生成物在质量门禁上整体豁免
* pytest `addopts` 含 `--strict-markers --strict-config --cov --cov-branch --import-mode=importlib`，即**每次跑 pytest
  都强制采集覆盖率**

### 7.2 Dockerfile（45 行，两阶段）

* builder：`python:3.14-slim` + `uv sync --frozen --no-editable --no-dev --package server`
* `--no-editable` 把 `server` 包实体安装进 `.venv`，因此运行层**不需要再 COPY 源码**——这是两阶段能只搬 `.venv` 的前提
* 运行层：非 root（uid/gid 1000），`EXPOSE 8000`，`GRANIAN_WORKERS=2`
* 构建上下文是仓库根（`Taskfile.yaml:206`），所以能 COPY 根 `pyproject.toml` + `uv.lock`

### 7.3 schemathesis.toml（7 行）

固定 `seed = 42` + `deterministic = true`，让契约测试可复现。

生效机制：`SchemathesisConfig.discover()` 从 **cwd** 逐级向上查找 `schemathesis.toml`，遇 `.git`
停止。`Taskfile.yaml:220-224` 的 `test-python` 用 `dir: apps/server` 运行，cwd 正好命中。

## 8. 测试策略

| 维度        | 做法                                                                                                   |
| ----------- | ------------------------------------------------------------------------------------------------------ |
| 分层        | `tests/` 严格镜像 `src/server/` 结构                                                                   |
| 单元        | `test_exceptions.py` 直接调函数，手搓最小 ASGI scope 构造 `Request` stub                               |
| 契约        | `test_router.py` 用 schemathesis 从 **dist 制品**生成用例，`case.call_and_validate(app=app)` ASGI 直连 |
| 可复现      | `schemathesis.toml` 固定 seed + deterministic                                                          |
| 覆盖率      | `addopts` 强制 `--cov --cov-branch`，`generated/` 豁免                                                 |
| 无 conftest | 全仓无 `conftest.py`，无共享 fixture                                                                   |

`test_router.py:13` 用 `parents[5]` 硬算仓库根指向
`contracts/http/dist/openapi.yaml`——测的是客户端实际消费的那份契约，但路径推算脆弱。

**未覆盖**：`core/logging.py`（149
行，含脱敏逻辑）、`core/config.py`、`core/bootstrap.py`、`api/router.py`、`api/deps.py`、`features/health/constants.py`
均无行为断言。这些模块只在 `from server.main import app` 时被 import
执行，覆盖率数字会「看起来很高」但没有任何断言保护。

## 9. 关键文件

| 文件                                                                             | 作用           |
| -------------------------------------------------------------------------------- | -------------- |
| [main.py](../apps/server/src/server/main.py)                                     | 应用入口       |
| [core/logging.py](../apps/server/src/server/core/logging.py)                     | 日志与脱敏     |
| [core/exceptions.py](../apps/server/src/server/core/exceptions.py)               | 异常体系       |
| [features/health/router.py](../apps/server/src/server/features/health/router.py) | 存活探针       |
| [generated/contracts.py](../apps/server/src/server/generated/contracts.py)       | 契约生成物     |
| [pyproject.toml](../apps/server/pyproject.toml)                                  | 依赖与工具配置 |
| [Dockerfile](../apps/server/Dockerfile)                                          | 镜像构建       |
