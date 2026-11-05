# Server 应用

FastAPI 服务的目录规范与代码编写说明新增代码按本文档放置

## 技术栈

* Web 框架：FastAPI
* ASGI 服务器：Granian
* 配置：pydantic-settings
* 日志：structlog
* 契约：OpenAPI + Schemathesis
* 检查：Ruff、ty、pytest

当前不包含数据库层；需要时再引入，并同步更新依赖、配置与本文件

## 目录结构

```text
apps/server/                      # Server 应用
├── src/                          # 源码
│   └── server/                   # 应用包
│       ├── api/                  # HTTP 层
│       │   ├── deps.py           # 共享依赖
│       │   └── router.py         # 路由聚合
│       ├── core/                 # 基础设施
│       │   ├── bootstrap.py      # 启动装配
│       │   ├── config.py         # 应用配置
│       │   ├── exceptions.py     # 异常定义
│       │   └── logging.py        # 日志配置
│       ├── features/             # 业务功能
│       │   └── health/           # 健康检查
│       │       └── router.py     # 存活探针
│       ├── generated/            # 契约生成物
│       │   └── contracts.py      # 契约模型
│       ├── __init__.py           # 包初始化
│       └── main.py               # 应用入口
├── tests/                        # 测试
│   ├── core/                     # 基础设施测试
│   │   └── test_exceptions.py    # 异常测试
│   └── features/                 # 业务功能测试
│       └── health/               # 健康检查测试
│           └── test_router.py    # 路由测试
├── pyproject.toml                # Python 项目配置
├── schemathesis.toml             # 契约模糊测试
└── Dockerfile                    # 容器镜像
```

`schemas/` 用于跨 feature 共享的 Pydantic 模型，按需创建

## 代码放置

| 要新增的内容           | 放置位置                                       |
| ---------------------- | ---------------------------------------------- |
| 应用入口与装配         | `src/server/main.py`                           |
| 启动装配               | `src/server/core/bootstrap.py`                 |
| 路由聚合               | `src/server/api/router.py`                     |
| 共享依赖               | `src/server/api/deps.py`                       |
| 业务 HTTP 路由         | `src/server/features/<domain>/router.py`       |
| 业务逻辑               | `src/server/features/<domain>/service.py`      |
| 业务请求/响应模型      | `src/server/features/<domain>/schemas.py`      |
| 业务依赖               | `src/server/features/<domain>/dependencies.py` |
| 业务异常               | `src/server/features/<domain>/exceptions.py`   |
| 业务常量               | `src/server/features/<domain>/constants.py`    |
| 跨域共享 Pydantic 模型 | `src/server/schemas/`                          |
| 配置、日志、异常基类   | `src/server/core/`                             |
| 契约生成物             | `src/server/generated/`                        |
| 测试                   | `tests/`，镜像源码结构                         |

补充规则：

* feature 内的 `router.py` 只负责 HTTP 入参与响应，复杂逻辑放 `service.py`
* 简单查询可以直接在 router 中完成，不强制创建空的 `service.py`
* 契约生成物禁止手改；修改 `contracts/http/openapi.yaml` 后重新生成
* 不要创建全局 `services/`、`modules/`、`utils/` 目录
* 当前没有 ORM 与数据库迁移；需要数据库时再单独引入，不要提前放置空目录

## 命名规范

| 对象          | 规则                                    | 示例                                   |
| ------------- | --------------------------------------- | -------------------------------------- |
| 目录/文件     | `snake_case`                            | `features/health/router.py`            |
| 类            | `PascalCase`                            | `Settings`、`AppError`                 |
| 函数/变量     | `snake_case`                            | `get_health`、`user_service`           |
| 常量          | `UPPER_SNAKE_CASE`                      | `DEFAULT_LOG_LEVEL`                    |
| 路由变量      | `router`                                | 每个 feature 一个                      |
| 聚合路由      | `api_router`                            | `api/router.py`                        |
| 依赖函数      | `get_*`                                 | `get_current_user`                     |
| 异常          | `*Error`                                | `AppError`、`UserNotFoundError`        |
| Pydantic 模型 | `XxxCreate` / `XxxUpdate` / `XxxPublic` | 不使用 `DTO` 或 `I` 前缀               |
| 测试          | `test_<subject>.py`                     | `tests/features/health/test_router.py` |
| 环境变量      | `APP_` + `UPPER_SNAKE_CASE`             | `APP_LOG_LEVEL`                        |

## 环境变量

| 变量             | 默认值    | 说明                |
| ---------------- | --------- | ------------------- |
| `APP_LOG_LEVEL`  | `INFO`    | 日志级别            |
| `APP_LOG_FORMAT` | `console` | `console` 或 `json` |

约定：

* 本地 `.env` 不提交；生产通过容器环境变量或密钥管理注入
* 当前只保留日志配置，不包含数据库连接配置

## 常用命令

```bash
# 安装依赖
mise exec -- just install

# 检查与测试
mise exec -- just check
mise exec -- just test-python

# 本地启动（在 apps/server 下）
mise exec -- uv run --locked granian --interface asgi --host 127.0.0.1 --port 8000 server.main:app

# 契约生成与漂移检查
mise exec -- just codegen
mise exec -- just check-codegen
```

## 代码要求

* 所有公开函数和方法需要类型注解与 docstring
* 业务异常统一继承 `AppError`，不要在路由中直接返回裸 `dict` 错误
* 使用 `structlog` 记录日志，不直接使用 `print`
* Ruff 规则已包含 `ANN`、`ARG`、`BLE`、`EM`、`G`、`LOG`、`PLR`、`PTH`、`SLF`、`TD`、`INP`
  等；提交前运行 `just check`
* Python import 使用 isort 规则，每个 import 独占一行
* 禁止手改 `src/server/generated/`
* 禁止在 feature 之间直接导入内部实现；跨域能力放 `core/` 或共享 `schemas/`
* 禁止提交 `.env` 与密钥
