# Contracts

TypeSpec 是契约源头，编译为 OpenAPI 3.1 制品。`vacuum` 校验制品，`oasdiff` 检查兼容性。

## 结构

```text
contracts/
├── typespec/
│   ├── main.tsp
│   ├── models/
│   │   ├── response.tsp
│   │   └── health.tsp
│   ├── routes/
│   │   └── health.tsp
│   └── tspconfig.yaml
├── http/
│   └── dist/
│       └── openapi.yaml
├── ruleset.yaml
└── README.md
```

## 文件职责

* `typespec/main.tsp`：服务入口，声明服务、服务器、版本与全局标签
* `typespec/models/`：数据模型，一文件一领域
* `typespec/routes/`：HTTP 路由与操作定义
* `typespec/tspconfig.yaml`：OpenAPI 3.1 emitter 配置，输出到 `http/dist/openapi.yaml`
* `http/dist/openapi.yaml`：OpenAPI 制品，由 `task compile-spec` 生成，禁止手改
* `ruleset.yaml`：契约检查规则，继承 `vacuum:oas` 推荐规则并追加敏感字段禁例

## 修改流程

1. 修改 `typespec/` 下的 `.tsp` 文件
2. 运行 `task compile-spec` 重新生成 `http/dist/openapi.yaml`
3. 运行 `task check-contract` 校验契约、制品与漂移
4. 提交 TypeSpec 源与 `dist/openapi.yaml`，保持两者一致

## 注意事项

* TypeSpec 固定为 `1.18.0`，输出 OpenAPI `3.1.0`
* 契约工具链使用 Bun `1.4.4`，通过 `bunx --bun` 运行 TypeSpec
* 使用 `@doc`、`@summary`、`@example`、`@opExample` 维护描述与示例
* `dist/` 由工具生成，禁止手改；`vacuum` 要求 `--min-score 95`
* 不要在契约中放置真实密钥；`vacuum` 会检查敏感字段的示例与默认值
* 修改契约后必须同步 `dist/openapi.yaml`，否则 `task check-contract` 会失败
* 当前未接入 server/web 代码生成与 schemathesis 测试；应用落地后再扩展

## 命名约定

| 对象     | 规则                | 示例                          |
| -------- | ------------------- | ----------------------------- |
| 模型文件 | 小写，领域名        | `response.tsp`、`health.tsp`  |
| 路由文件 | 小写，资源名或 slug | `health.tsp`、`users.tsp`     |
| 模型名   | PascalCase          | `HealthzResponse`、`Response` |
| 操作名   | camelCase           | `getHealthz`、`listUsers`     |
| 标签     | 小写                | `health`、`users`             |
| 规则文件 | `ruleset.yaml`      | 位于契约根目录                |

## 常用命令

```bash
# 安装契约依赖
task install-typespec

# 生成 OpenAPI 制品
task compile-spec

# 校验契约
task check-api

# 检查契约漂移
task check-contract

# 运行完整检查
task check
```
