# Contracts

跨端 API 契约源头OpenAPI 契约经过打包、校验和代码生成，产出 server 的 Pydantic 模型与 web 的
TypeScript 客户端

## 结构

```text
contracts/                    # 契约
└── http/                     # HTTP 契约
    ├── components/           # 组件
    │   ├── responses.yaml    # 响应定义
    │   └── schemas.yaml      # 模式定义
    ├── dist/                 # 打包制品
    │   └── openapi.yaml      # 打包结果
    ├── paths/                # 路径定义
    │   └── healthz.yaml      # 存活探针
    ├── openapi.yaml          # 契约入口
    └── vacuum.yaml           # 规则集
```

## 文件职责

* `http/openapi.yaml`：契约入口，声明 OpenAPI 版本、信息、服务器与路径引用
* `http/paths/`：按资源域拆分的路径文件，每个文件对应一个资源或探针
* `http/components/`：可复用响应与模式，统一响应信封放在 `schemas.yaml`
* `http/dist/openapi.yaml`：打包制品，由 `just bundle` 生成，禁止手改
* `http/vacuum.yaml`：契约检查规则，继承 `vacuum:oas` 推荐规则并追加敏感字段禁例

## 修改流程

1. 修改 `http/openapi.yaml`、`http/paths/` 或 `http/components/`
2. 运行 `just bundle` 重新打包 `dist/openapi.yaml`
3. 运行 `just codegen` 重新生成 server 与 web 的契约代码
4. 运行 `just check-api`、`just check-codegen` 和相关测试
5. 提交契约源头与生成物，保持两者一致

## 注意事项

* `openapi.yaml` 使用 OpenAPI 3.1.2，JSON Schema 方言为 2020-12
* 新增接口时先在 `paths/` 增加资源文件，再在入口 `paths` 下用 `$ref` 引用
* 响应统一使用 `Response` 信封：`code`、`message`、`data`，并设置 `additionalProperties: false`
* `dist/` 与两个应用的生成物都由工具生成，禁止手改
* server 生成物：`apps/server/src/server/generated/contracts.py`
* web 生成物：`apps/web/src/api/generated/http` 与 `apps/web/src/api/generated/schemas`
* `just bundle` 会统一写入 LF 换行，避免 Windows CRLF 漂移
* 不要在契约中放置真实密钥；`vacuum` 会检查敏感字段的示例与默认值
* 修改契约后必须同步生成物，否则 `just check-codegen` 会失败

## 常用命令

```bash
# 打包契约
mise exec -- just bundle

# 生成 server / web 契约代码
mise exec -- just codegen

# 检查生成物漂移
mise exec -- just check-codegen

# 校验 OpenAPI 契约
mise exec -- just check-api

# 运行完整检查与测试
mise exec -- just check
mise exec -- just test
```
