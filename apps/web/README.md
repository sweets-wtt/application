# Web 应用

Vue 3 单页应用的目录规范与代码编写说明新增代码按本文档放置，避免后期再次迁移

## 技术架构

```text
应用: web
├── 运行时: bun
├── 框架: vue
├── 构建工具: vite
├── 语言: typescript
├── 路由: vue-router
├── 状态管理: pinia
├── 状态持久化: pinia-plugin-persistedstate
├── 数据请求: @tanstack/vue-query
├── 组合式工具: @vueuse/core
├── 契约客户端: orval
├── 模式校验: zod
├── 样式: unocss
├── 图标: @iconify-json/carbon
├── 组件库: reka-ui
├── 日志: consola
└── 开发工具
    ├── 类型检查: typescript
    ├── 单元测试: vitest
    ├── 测试环境: jsdom
    ├── 组件测试: @vue/test-utils
    ├── 端到端测试: playwright
    ├── 体积检查: size-limit
    ├── 构建插件: @vitejs/plugin-vue
    ├── 自动导入: unplugin-auto-import
    ├── 图标按需: unplugin-icons
    └── 组件按需: unplugin-vue-components
```

## 目录结构

```text
apps/web/                                # 前端应用
├── src/                                 # 源码目录
│   ├── api/                             # 接口访问
│   │   ├── generated/                   # 契约生成
│   │   │   ├── http/                    # 接口生成
│   │   │   │   ├── default/             # 默认分组
│   │   │   │   │   └── default.ts       # 实现文件
│   │   │   │   └── index.ts             # 出口文件
│   │   │   └── schemas/                 # 模式校验
│   │   │       └── index.zod.ts         # 模式出口
│   │   ├── client.ts                    # 请求封装
│   │   └── index.ts                     # 接口导出
│   ├── config/                          # 环境配置
│   │   └── env.ts                       # 环境变量
│   ├── features/                        # 业务功能
│   │   └── health/                      # 健康检查
│   │       ├── composables/             # 组合函数
│   │       │   └── useHealthCheck.ts    # 健康检查
│   │       ├── constants.ts             # 常量定义
│   │       └── index.ts                 # 模块出口
│   ├── layouts/                         # 页面布局
│   │   └── DefaultLayout.vue            # 默认布局
│   ├── lib/                             # 通用工具
│   │   ├── logger.ts                    # 日志工具
│   │   ├── query.ts                     # 查询封装
│   │   └── storage.ts                   # 存储工具
│   ├── router/                          # 路由目录
│   │   ├── index.ts                     # 路由实例
│   │   └── routes.ts                    # 路由定义
│   ├── stores/                          # 状态仓库
│   │   ├── app.ts                       # 应用状态
│   │   └── index.ts                     # 状态实例
│   ├── styles/                          # 全局样式
│   │   └── main.css                     # 主样式表
│   ├── views/                           # 页面目录
│   │   └── HomeView.vue                 # 首页页面
│   ├── env.d.ts                         # 环境类型
│   ├── main.ts                          # 应用入口
│   └── App.vue                          # 根级组件
├── tests/                               # 测试目录
│   ├── e2e/                             # 端到端测
│   │   └── smoke.spec.ts                # 冒烟测试
│   ├── unit/                            # 单元测试
│   │   ├── api/                         # 接口测试
│   │   │   ├── client.test.ts           # 请求测试
│   │   │   └── index.test.ts            # 导出测试
│   │   ├── features/                    # 业务测试
│   │   │   └── health/                  # 健康测试
│   │   │       └── constants.test.ts    # 常量测试
│   │   ├── lib/                         # 工具测试
│   │   │   ├── logger.test.ts           # 日志测试
│   │   │   └── storage.test.ts          # 存储测试
│   │   ├── router/                      # 路由测试
│   │   │   └── router.test.ts           # 路由测试
│   │   ├── stores/                      # 状态测试
│   │   │   └── app.test.ts              # 状态测试
│   │   └── App.test.ts                  # 组件测试
│   └── setup.ts                         # 测试配置
├── .env.example                         # 变量示例
├── index.html                           # 页面模板
├── nginx.conf                           # 代理配置
├── orval.config.ts                      # 契约配置
├── package.json                         # 包体配置
├── playwright.config.ts                 # 端到端配
├── tsconfig.json                        # 脚本配置
├── uno.config.ts                        # 样式配置
├── vite.config.ts                       # 构建配置
└── Dockerfile                           # 容器镜像
```

> 本文档定义目标结构迁移期间新旧路径可能短暂并存；新增代码直接使用目标路径，迁移完成后删除旧路径

## 代码放置

| 要新增的内容   | 放置位置                                      |
| -------------- | --------------------------------------------- |
| 应用入口       | `src/main.ts`                                 |
| 根组件         | `src/App.vue`                                 |
| 页面           | `src/views/XxxView.vue`                       |
| 布局           | `src/layouts/XxxLayout.vue`                   |
| 通用组件       | `src/components/`                             |
| 通用组合式函数 | `src/composables/useXxx.ts`                   |
| 业务模块       | `src/features/<domain>/`                      |
| 业务组件       | `src/features/<domain>/components/`           |
| 业务组合式函数 | `src/features/<domain>/composables/useXxx.ts` |
| 业务 API 封装  | `src/features/<domain>/api.ts`                |
| 业务常量       | `src/features/<domain>/constants.ts`          |
| 业务类型       | `src/features/<domain>/types.ts`              |
| HTTP 客户端    | `src/api/client.ts`                           |
| 契约生成物     | `src/api/generated/`                          |
| 环境配置       | `src/config/env.ts`                           |
| 通用工具       | `src/lib/`                                    |
| 路由定义       | `src/router/routes.ts`                        |
| 路由实例       | `src/router/index.ts`                         |
| 状态仓库       | `src/stores/`                                 |
| 全局样式       | `src/styles/`                                 |
| 全局类型       | `src/types/`                                  |
| 单元测试       | `tests/unit/`，镜像源码结构                   |
| 端到端测试     | `tests/e2e/`                                  |

补充规则：

* 页面统一放 `views/`，不要同时使用 `pages/`
* 通用能力统一放 `lib/` 和 `config/`，不要同时使用 `core/`、`shared/`
* 业务代码放 `features/<domain>/`，不要按 `components/`、`api/`、`stores/` 横向拆散业务
* 通用组件和业务组件分开：跨 feature 复用的放 `src/components/`
* 组合式函数统一使用 `composables/`，不要使用 `hooks/`
* 契约生成物禁止手改；修改 `contracts/http/openapi.yaml` 后重新生成
* 不要创建 `utils/`、`helpers/` 作为无边界聚合目录

## 命名规范

| 对象             | 规则                            | 示例                                |
| ---------------- | ------------------------------- | ----------------------------------- |
| 目录             | `kebab-case`                    | `features/health`                   |
| Vue 组件         | `PascalCase.vue`                | `HomeView.vue`、`DefaultLayout.vue` |
| 页面             | `XxxView.vue`                   | `HomeView.vue`                      |
| 布局             | `XxxLayout.vue`                 | `DefaultLayout.vue`                 |
| Composable       | `useXxx.ts` / `useXxx()`        | `useHealthCheck.ts`                 |
| Pinia store      | `useXxxStore`                   | `useAppStore`                       |
| 普通 TS 文件     | 小写或 `kebab-case.ts`          | `env.ts`、`logger.ts`               |
| 类型/接口        | `PascalCase`，无 `I`/`T` 前缀   | `PersistedState`                    |
| 函数/变量        | `camelCase`                     | `apiFetch`、`parseState`            |
| 常量             | `UPPER_SNAKE_CASE`              | `API_BASE_URL`                      |
| 布尔             | `is` / `has` / `can` / `should` | `isVisible`                         |
| 事件处理         | `handleXxx`                     | `handleSubmit`                      |
| Props/Emits 类型 | `XxxProps` / `XxxEmits`         | `BaseButtonProps`                   |
| 单元测试         | `*.test.ts`                     | `tests/unit/lib/logger.test.ts`     |
| 端到端测试       | `*.spec.ts`                     | `tests/e2e/smoke.spec.ts`           |

## 环境变量

| 变量                      | 默认值  | 说明                       |
| ------------------------- | ------- | -------------------------- |
| `VITE_API_BASE_URL`       | 空      | API 基地址；空表示同源     |
| `VITE_HEARTBEAT_INTERVAL` | `30000` | 健康检查轮询间隔，单位毫秒 |

约定：

* 所有 `VITE_*` 变量都会进入客户端 bundle，不能存放密钥
* 生产环境默认同源，由 Nginx 反代 API
* 本地开发可设置绝对 API 地址，或在 Vite 中配置 `/healthz`、`/api` 代理，保持与生产同源
* 环境变量统一在 `src/config/env.ts` 解析，业务代码不直接读 `import.meta.env`

## 常用命令

```bash
# 安装依赖
mise exec -- task install

# 检查与测试
mise exec -- task check-typescript
mise exec -- task test-typescript
mise exec -- task test-e2e
mise exec -- task check-size

# 本地开发（在 apps/web 下）
bun run dev
bun run build
bun run preview

# 契约生成与漂移检查
mise exec -- task codegen
mise exec -- task check-codegen
```

## 代码要求

* TypeScript 严格模式，禁止 `any`
* 类型导入使用 `import type`，与 oxlint 规则保持一致
* 业务日志统一使用 `lib/logger`，不直接使用 `console`
* 组件使用 `<script setup lang="ts">`，props/emits 显式声明类型
* 业务请求通过 feature 的 `api.ts` 或生成的契约客户端发起，不在组件中直接拼接 URL
* 不手改 `src/api/generated/`
* 不重复定义契约模型；需要新类型时先改 OpenAPI 并重新生成
* 提交前运行 `mise exec -- task check` 与 `mise exec -- task test`
* 禁止提交 `.env`、密钥、构建产物
