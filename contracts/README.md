# Contracts

跨端 API 契约源头，OpenAPI 契约经过打包、校验和代码生成，产出 server 的 Pydantic 模型与 web 的 TypeScript 客户端

## 结构

```text
contracts/                         # 契约目录
├── grpc/                          # 远程调用
│   └── proto/                     # 协议定义
├── graphql/                       # 查询语言
├── http/                          # 接口契约
│   ├── components/                # 组件目录
│   │   ├── parameters/            # 共享参数
│   │   ├── responses/             # 响应定义
│   │   │   └── Healthz200.yaml    # 存活响应
│   │   ├── schemas/               # 模式定义
│   │   │   └── Response.yaml      # 响应信封
│   │   └── securitySchemes/       # 认证方案
│   ├── dist/                      # 打包制品
│   │   └── openapi.yaml           # 打包结果
│   ├── examples/                  # 接口样例
│   ├── paths/                     # 路径定义
│   │   └── healthz.yaml           # 存活探针
│   └── openapi.yaml               # 契约入口
├── ruleset.yaml                   # 契约规则
└── README.md                      # 契约说明
```

空目录仅在需要时创建，文件均需实际存在

## 文件职责

* `http/openapi.yaml`：契约入口，声明 OpenAPI 版本、信息、服务器与路径引用
* `http/paths/`：按资源域拆分的路径文件，每个文件对应一个资源或探针
* `http/components/schemas/`：一组件一文件，文件名使用组件名
* `http/components/responses/`：一响应一文件，文件名使用响应名
* `http/dist/openapi.yaml`：打包制品，由 `task bundle-spec` 生成，禁止手改
* `ruleset.yaml`：跨协议共享的契约检查规则，继承 `vacuum:oas` 推荐规则并追加敏感字段禁例

## 修改流程

1. 修改 `http/openapi.yaml`、`http/paths/` 或 `http/components/`
2. 运行 `task bundle-spec` 重新打包 `dist/openapi.yaml`
3. 运行 `task codegen` 重新生成 server 与 web 的契约代码
4. 运行 `task check-api`、`task check-codegen` 和相关测试
5. 提交契约源头与生成物，保持两者一致

## 注意事项

* `openapi.yaml` 使用 OpenAPI 3.1.2，JSON Schema 方言为 2020-12
* 新增接口时先在 `paths/` 增加资源文件，再在入口 `paths` 下用 `$ref` 引用
* 新增组件时在 `components/` 对应目录单独建文件，不要聚合到单个文件
* 组件引用使用相对路径，例如 `../components/responses/Healthz200.yaml`
* 响应统一使用 `Response` 信封：`code`、`message`、`data`，并设置 `additionalProperties: false`
* 内部单仓库不建版本目录；需要多版本并存时用 Redocly 别名而不是 `v1/`
* `dist/` 与两个应用的生成物都由工具生成，禁止手改
* server 生成物：`apps/server/src/server/generated/contracts.py`
* web 生成物：`apps/web/src/api/generated/http` 与 `apps/web/src/api/generated/schemas`
* `task bundle-spec` 会统一写入 LF 换行，避免 Windows CRLF 漂移
* 不要在契约中放置真实密钥；`vacuum` 会检查敏感字段的示例与默认值
* 修改契约后必须同步生成物，否则 `task check-codegen` 会失败

## 命名约定

| 对象     | 规则                | 示例                                  |
| -------- | ------------------- | ------------------------------------- |
| 协议目录 | 小写                | `http`、`grpc`、`graphql`             |
| 路径文件 | 小写，资源名或 slug | `healthz.yaml`、`users_{userId}.yaml` |
| 组件文件 | 组件名原样          | `Response.yaml`、`Healthz200.yaml`    |
| 入口文件 | `openapi.yaml`      | 不使用 `api.yaml` 或 `swagger.yaml`   |
| 打包目录 | `dist/`             | 不使用 `build/`                       |
| 规则文件 | `ruleset.yaml`      | 位于契约根目录                        |

## 常用命令

```bash
# 打包契约
mise exec -- task bundle-spec

# 生成 server / web 契约代码
mise exec -- task codegen

# 检查生成物漂移
mise exec -- task check-codegen

# 校验 OpenAPI 契约
mise exec -- task check-api

# 运行完整检查与测试
mise exec -- task check
mise exec -- task test
```
