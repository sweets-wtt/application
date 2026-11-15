# apps/web（Vue 前端）

## 1. 定位

`apps/web` 是一个**极简的 Vue 3 + Vite 单页应用骨架**：唯一的业务功能是「首页 +
服务端存活状态指示灯」。它的价值不在功能，而在于把工程规范（目录约定、契约生成、严格
TS、版本化持久化、日志脱敏、测试分层）全部搭好并跑通一条端到端竖切，作为后续业务代码的模板。

源码 `src/` 共 22 个文件约 900 行，测试 11 个文件约 12.8 KB。

## 2. 目录与职责

```
apps/web/
├── src/
│   ├── api/          client.ts（fetch 封装）+ generated/（orval 产物）+ index.ts（桶）
│   ├── config/       env.ts（唯一读 import.meta.env 的地方）
│   ├── features/     health/（composables + constants + index）
│   ├── layouts/      DefaultLayout.vue
│   ├── lib/          logger.ts / query.ts / storage.ts
│   ├── router/       index.ts（实例）/ routes.ts（表）
│   ├── stores/       index.ts（pinia 实例）/ app.ts（唯一 store）
│   ├── styles/       main.css
│   ├── views/        HomeView.vue
│   ├── env.d.ts      *.vue 模块声明 + ImportMetaEnv
│   ├── main.ts       入口
│   └── App.vue       根组件
├── tests/            setup.ts + unit/（镜像 src 结构）+ e2e/
├── index.html  vite.config.ts  uno.config.ts  tsconfig.json
├── orval.config.ts  playwright.config.ts  package.json
├── components.d.ts（unplugin-vue-components 生成，已提交）
└── Dockerfile  .env.example  README.md
```

**分层规则**（`README.md:110-146`）是硬约定：

| 内容        | 位置                                                                           |
| ----------- | ------------------------------------------------------------------------------ |
| 页面 / 布局 | `src/views/XxxView.vue` / `src/layouts/XxxLayout.vue`                          |
| 业务代码    | `src/features/<domain>/`（**不按 components/api/stores 横向拆散**）            |
| 通用能力    | `src/lib/`、`src/config/`（**禁止** `core/`、`shared/`、`utils/`、`helpers/`） |
| 组合式函数  | 一律 `composables/useXxx.ts`（**禁止** `hooks/`）                              |
| 契约生成物  | `src/api/generated/`，**禁止手改**                                             |

**README 里规划但当前不存在的目录**：`src/components/`、`src/composables/`、`src/types/`。`vite.config.ts:13-17` 的
`unplugin-vue-components` 默认扫描 `src/components`，该目录缺失意味着自动组件注册目前是空转。

## 3. 启动链路

```
index.html:9   <div id="app"></div>
index.html:10  <script type="module" src="/src/main.ts"></script>
   ↓
main.ts:12     import "@/styles/main.css"        ← 先重置样式
main.ts:13     import "virtual:uno.css"          ← 后注入原子类（顺序正确）
main.ts:16     configureLogger()                 ← 日志（实为空操作）
main.ts:19     setBaseUrl(API_BASE_URL)          ← 必须在首次请求前
main.ts:22     const app = createApp(App)
main.ts:25     app.use(pinia)                    ← pinia 已装持久化插件
main.ts:28     app.use(router)
main.ts:31     app.use(VueQueryPlugin, { queryClient })
main.ts:34     app.mount("#app")
   ↓
App.vue:4      <RouterView />
   ↓  router 匹配 "/" → redirect "/home"
DefaultLayout.vue:4  <RouterView />              ← 布局层再套一层出口
   ↓
HomeView.vue:7 const { status } = useHealthCheck()
   ↓
useHealthCheck.ts:65  useGetHealthz({ query: { enabled, refetchInterval, retry } })
   ↓
health.ts:40   apiFetch<getHealthzResponse>("/healthz", { method: "GET" })
   ↓
client.ts:116  fetch(`${baseUrl}${path}`, init)
```

### 插件注册要点

* **pinia**：`stores/index.ts:5-7` 先 `createPinia()` 再 `pinia.use(piniaPluginPersistedstate)`，`main.ts:25` 才
  `app.use(pinia)`。持久化是**插件级全局注册**，具体策略在 store 上声明。
* **vue-router**：`createRouter({ history: createWebHistory(), routes })`，**无任何导航守卫**。
* **vue-query**：传入自定义 `queryClient`（`lib/query.ts:4-11`），而非用默认实例。
* **UnoCSS 不是 Vue 插件**，是 **Vite 插件**（构建期），运行时靠 `virtual:uno.css` 注入。
* **`components.d.ts`** 只声明了 `RouterLink` / `RouterView`，说明目前**零个自定义组件被自动注册**。

### 双层空壳

`App.vue` 与 `DefaultLayout.vue` 内容完全一致（都只有 `<RouterView />`），`App → RouterView → DefaultLayout → RouterView
→ HomeView` 多了一层无意义嵌套。布局层目前不提供任何 header/nav/footer，属于「为将来预留」的占位。

## 4. api 层

### 4.1 client.ts（126 行，手写）

**baseURL 是模块级可变单例**，无 URL 拼接容错：

```ts
let baseUrl = "";
export const setBaseUrl = (value: string): void => { baseUrl = value; };
const response = await fetch(`${baseUrl}${path}`, init);
```

若 `baseUrl` 以 `/` 结尾且 `path` 以 `/` 开头会得到 `//healthz`。当前 `env.ts` 默认空串、`path` 恒以 `/`
开头，暂不触发。

**错误处理：只抛状态码 + 路径，丢弃响应体**：

```ts
if (!response.ok) {
  throw new Error(`${response.status} ${path}`);
}
```

后端统一信封里的 `message` 拿不到，前端无法区分业务错误码。**无拦截器机制**、**无超时**（未用
`AbortSignal.timeout`）、**无 `credentials`/`Accept` 头**。

**响应体解析按 content-type 分派**：

* 204/205 → `undefined`
* `application/json` → `response.json()`
* 非 text 的 content-type → `response.blob()`
* 其余 → 文本（空串转 `undefined`）

**可测试性设计（值得肯定）**：`ResponseView` 接口只声明解析用到的 5 个成员，让测试可以传鸭子类型对象而不必构造真
`Response`。

**Orval 约定信封 + 不可避免的类型断言**：`apiFetch` 返回 `{ data, headers, status }`，末尾 `as TData`。

### 4.2 generated/（orval 产物）

生成链路：`contracts/http/openapi.yaml` →（`bundle-spec`）→ `contracts/http/dist/openapi.yaml` →（`bunx orval`）→
`src/api/generated/`。

`orval.config.ts` 关键配置：

```ts
target: "../../contracts/http/dist/openapi.yaml",
client: "vue-query",
mode: "tags-split",
mutator: { name: "apiFetch", path: "./src/api/client.ts" },
schemas: { mode: "single", path: "./src/api/generated/schemas", type: "zod" },
```

产物结构（`mode: "tags-split"` → 按 OpenAPI tag 分目录）：

| 文件                                       | 内容                                                                                   |
| ------------------------------------------ | -------------------------------------------------------------------------------------- |
| `generated/http/health/health.ts`（89 行） | tag=`health` 的全部产物：URL 构造器、裸请求函数、queryKey、queryOptions、`useXxx` hook |
| `generated/http/index.ts`（1 行）          | `export * from "./health/health";`                                                     |
| `generated/schemas/index.zod.ts`（20 行）  | `mode: "single"` 把所有 schema 收进一个文件                                            |

`health.ts` 的 5 段结构：响应类型（按状态码枚举）→ URL 构造器 → 裸请求（走 mutator）→ queryKey + queryOptions → Vue
hook。

`schemas/index.zod.ts` 只有两个 schema，且 `Healthz200Response` 用 `.and()` 表达 OpenAPI 的 `allOf`：

```ts
export const Response = zod.object({ code: zod.int(), message: zod.string(), data: zod.looseObject({}) });
export const Healthz200Response = Response.and(
  zod.object({ data: zod.object({ status: zod.enum(["ok"]) }) }),
);
```

每个 schema 同时导出 `zod.input` / `zod.output` 两个类型。

> **重要取舍**：zod schema **没有接进 `apiFetch`**（mutator 只做
> fetch，不做校验）。运行时校验是业务层手动调用的。也就是说「契约生成」只保证了**类型**，**不保证运行时数据合法**，除非每个
> composable 自己 `safeParse`。

### 4.3 index.ts（3 行桶）

导出 `setBaseUrl` / `getBaseUrl` / `apiFetch` / `ResponseView` / `getHealthz` / `useGetHealthz` /
`getGetHealthzQueryKey` / `getGetHealthzQueryOptions` / `Response` / `Healthz200Response` 及各自类型。

> **潜在坑**：`index.zod.ts` 导出的 `Response` 常量/类型会**遮蔽 DOM 全局 `Response`**。任何 `import { Response } from
> "@/api"` 的文件里 `new Response(...)` 会失效。目前 `client.ts` 不 import 桶，尚未踩到。

## 5. lib 三件套

### 5.1 logger.ts（137 行）

设计意图：**应用不直接依赖 Consola**，只暴露 `error/info/warn` 三个方法。

* `SENSITIVE_KEYS` 与后端一致：`password` / `secret` / `token` / `authorization` / `api_key`
* `maskValue` 命中键名返回 `"***"`
* **无 console 环境降级为空实现**（`globalThis.console === undefined` 时返回 `undefined`）
* 默认级别 3（info）

> `configureLogger()` 是**空操作**：它只是 `configure(DEFAULT_LOG_LEVEL)`，而 `createInstance`
> 已经用同一个级别建实例。`main.ts:16` 的调用没有任何实际效果。
>
> `redact` 只脱敏**顶层键**：`logger.info("x", { user: { token: "abc" } })` 里的 token 不会被掩码。也没有
> `debug`/`trace` 方法。

### 5.2 query.ts（13 行）

只改了一个默认项：`refetchOnWindowFocus: false`。**没有** `staleTime` / `gcTime` / 全局 `retry` / 全局
`onError`。轮询参数由 `useHealthCheck` 自己传。

### 5.3 storage.ts（190 行）

全仓**最"重"的一个文件**，实现了完整的「读 → 解析 → 逐级迁移 → 校验 → 回退」管线。

```ts
export const STORAGE_KEY = "app";
const CURRENT_VERSION = "1";
const DEFAULT_VERSION = "0";        // 无 version 字段视为最早版本
const MAX_MIGRATION_STEPS = 16;     // 防迁移表成环
const stateSchema = z.object({ locale: z.enum(["zh-CN", "en-US"]), version: z.literal(CURRENT_VERSION) });
export const defaultState: State = { locale: "zh-CN", version: CURRENT_VERSION };
const migrations: Record<string, (state) => Record<string, unknown>> = {};   // ← 空表
```

迁移主循环：版本不匹配时查 `migrations[version]`，查不到就 `settle` 返回 `undefined`；查到就执行并重读版本，靠
`MAX_MIGRATION_STEPS` 兜底防环。

`settle` 只在 `version === CURRENT_VERSION` 时返回数据，否则 `undefined`。

解析入口 `parseState`：非字符串 → `defaultState`；JSON 损坏 → `defaultState`；迁移失败或结构不符 → `defaultState`。

存储边界抽象只依赖 `getItem`/`setItem` 两个能力，便于测试注入内存实现。

> 这套机制目前**没有真实消费者**，详见 [findings.md](./findings.md) 问题 4。

## 6. router 与 stores

### 6.1 router

```ts
const router = createRouter({ history: createWebHistory(), routes });
```

路由表只有一条根路由：`path: "/"` → 懒加载 `DefaultLayout` → `redirect: "/home"` → 子路由 `home` → 懒加载
`HomeView`，`meta: { title: "首页" }`。

* **守卫：完全没有。** 无 `beforeEach` / `afterEach` / `beforeEnter`，无鉴权、无标题同步、无进度条。
* **没有 catch-all 404 路由**，未知路径会渲染空白页。
* **`meta.title` 是死元数据**：定义了但没有任何 `afterEach` 去写 `document.title`，`index.html` 的 `<title>应用</title>`
  永远不变。
* **懒加载写法冗余**：`component: async () => await import(...)`——`import()` 本身返回 Promise，`async/await` 是多余的。

### 6.2 stores

```ts
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);
```

```ts
const useAppStore = defineStore("app", () => ({}), {
  persist: {
    serializer: {
      deserialize: (raw) => parseState(raw),
      serialize: (state) => serializeState(state),
    },
    storage: stateStorage,   // localStorage 适配
  },
});
```

**状态：空对象 `{}`**。持久化策略：自定义 `serializer` 把读写都转交给 `lib/storage.ts` 的版本化管线，存储介质为
`localStorage`，key 为 `"app"`。

> 这里存在**形状不一致**：`parseState` 返回 `{locale, version}`，而 store 的 state 是 `{}`。详见
> [findings.md](./findings.md) 问题 4。

## 7. features/health 与页面

### 7.1 useHealthCheck.ts（94 行）

```ts
const RETRY_COUNT = 1;

export const useHealthCheck = (): HealthCheckResult => {
  const visibility = useDocumentVisibility();                       // @vueuse/core
  const enabled = computed(() => visibility.value === "visible");   // 页面隐藏时暂停轮询
  const { isSuccess, isError, isFetching, data: result } = useGetHealthz({
    query: { enabled, refetchInterval: HEARTBEAT_INTERVAL, retry: RETRY_COUNT },
  });
```

状态推导：`isSuccess` → `online`；`isError` → `offline`；否则 `checking`。

**契约校验（手动，非自动）**：`Healthz200Response.safeParse(payload)`，失败只 `logger.warn`
上报问题数量，不中断渲染，返回 `undefined`。

返回接口：`{ status, online, isFetching, data }`，全部是 `ComputedRef` / `Ref`。

### 7.2 constants.ts（41 行）

```ts
export const DEFAULT_HEARTBEAT_INTERVAL = 30_000;

export const parseHeartbeatInterval = (raw?: string): number => {
  const value = Number(raw);
  if (!Number.isFinite(value) || value <= MIN_INTERVAL) { return DEFAULT_HEARTBEAT_INTERVAL; }
  return value;
};

export const HEARTBEAT_INTERVAL = parseHeartbeatInterval(import.meta.env.VITE_HEARTBEAT_INTERVAL);

export const SERVER_STATUS = { checking: "checking", offline: "offline", online: "online" } as const;
export type ServerStatus = (typeof SERVER_STATUS)[keyof typeof SERVER_STATUS];
```

`parseHeartbeatInterval` 的注释点明了一个真实陷阱：**构建时注入空值 `VITE_HEARTBEAT_INTERVAL=`
会得到空串，`Number("") === 0`，轮询会被静默关闭**。这是本仓写得最"有信息量"的一段注释。

### 7.3 HomeView.vue（48 行）

* `const { status } = useHealthCheck()`
* `statusClass` 计算属性：online → `bg-green-500`、offline → `bg-red-500`、其余 → `bg-gray-400 animate-pulse`
* 模板：`<h1 class="text-2xl font-bold">首页</h1>` + 一个 `h-2.5 w-2.5 rounded-full` 圆点 + 文案（服务端在线 /
  服务端离线 / 连接中...）
* **纯 UnoCSS 原子类，无 scoped style，无组件拆分**

只解构了 `status`，`data` / `online` / `isFetching` 全部未使用；且 `SERVER_STATUS` 从 `@/features/health/constants`
直接导入，而 `@/features/health` 桶已经 re-export 了它——同一模块两种导入风格并存。

## 8. 工程配置

### 8.1 vite.config.ts（33 行）

* 从 `vitest/config` 导入 `defineConfig`，测试配置与构建配置同文件
* plugins：`vue()`、`UnoCSS()`、`Components({ dts: "./components.d.ts", resolvers: [IconsResolver({ prefix: "icon" }),
  RekaResolver()] })`、`Icons({ autoInstall: false })`
* alias：`"@" → ${import.meta.dirname}/src`
* test：`environment: "jsdom"`、`exclude: ["**/e2e/**", "**/node_modules/**"]`、`include:
  ["tests/**/*.test.ts"]`、`pool: "threads"`、`setupFiles: ["./tests/setup.ts"]`、`testTimeout: 5000`
* **没有 `server` 块**（无 proxy、无 port）、**没有 `build` 块**、**没有 `base`**

### 8.2 uno.config.ts（4 行）

```ts
export default defineConfig({ presets: [presetWind3(), presetIcons()] });
```

只有两个预设，**无 theme / shortcuts / safelist / transformers**。`presetIcons()` 未指定 collections，依赖
`@iconify-json/carbon` 自动发现。

### 8.3 tsconfig.json（69 行）—— 极严格

| 选项                                           | 效果                           |
| ---------------------------------------------- | ------------------------------ |
| `verbatimModuleSyntax: true`                   | 强制 `import type`             |
| `erasableSyntaxOnly: true`                     | 禁 enum / namespace / 参数属性 |
| `strict: true`                                 | —                              |
| `noUncheckedIndexedAccess: true`               | `arr[0]` 类型含 `undefined`    |
| `exactOptionalPropertyTypes: true`             | `x?: T` 不接受显式 `undefined` |
| `noPropertyAccessFromIndexSignature: true`     | 索引签名必须 `obj["k"]`        |
| `types: ["node", "vitest/globals"]`            | —                              |
| `paths: { "@/*": ["./src/*"] }`                | 无 `baseUrl`                   |
| `include: ["src", "tests", "components.d.ts"]` | **不含任何 `*.config.ts`**     |

### 8.4 playwright.config.ts

```ts
export default defineConfig({
  retries: 0,
  testDir: "./tests/e2e",
  use: { screenshot: "off", trace: "off", video: "off" },
  webServer: { command: "bun run preview", port: 4173, reuseExistingServer: !isCI },
});
```

### 8.5 package.json

scripts：`dev` / `build` / `preview` / `test`（`vitest run`）/ `size`（`size-limit`）。

**没有** `lint` / `typecheck` / `test:e2e` / `codegen` 脚本——这些全部由根 `Taskfile.yaml` 驱动。

体积预算：`{ "path": "dist/assets/index-*.js", "limit": "250 KB" }`。

值得注意的版本：`typescript ^7.0.2`、`vite ^8.3.8`、`vitest ^5.1.0`、`vue-router ^5.5.0`、`pinia ^4.1.0`、`zod ^4.6.7`。

### 8.6 其他

* **index.html**（12 行）：`lang="zh-CN"`、`<title>应用</title>`、`<div id="app">`、`<script type="module"
  src="/src/main.ts">`。无 favicon、无 `<noscript>`、无 preconnect。
* **components.d.ts**（17 行）：`unplugin-vue-components` 生成，**已提交入库**，由 Taskfile `build-types` 通过 `bun run
  build` 重新生成。
* **Dockerfile**（58 行）：两阶段。builder 用 `oven/bun:1`，`ARG VITE_API_BASE_URL` / `ARG VITE_HEARTBEAT_INTERVAL` 转
  `ENV` → 复制根 `package.json bun.lock` + `apps/web/*` → `bun install --frozen-lockfile` → `bun run build`。运行层用
  `caddy:2.11.9@sha256:e40b94d0...`（**digest 固定**），`COPY --from=builder /app/apps/web/dist /srv`，`COPY
  infra/Caddyfile`，建 uid 1000 的 `caddy` 用户、`setcap cap_net_bind_service=+ep`、`USER caddy`、`EXPOSE 80 443
  443/udp`。
* **.env.example**：`VITE_API_BASE_URL=`（空）、`VITE_HEARTBEAT_INTERVAL=30000`。
* **src/env.d.ts**：`*.vue` 模块声明 + `ImportMetaEnv { VITE_API_BASE_URL?: string; VITE_HEARTBEAT_INTERVAL?: string
  }`。
* **src/styles/main.css**（15 行）：`* { margin:0; padding:0; box-sizing:border-box }`、`html,body,#app { height:100%
  }`、系统字体栈。

## 9. 测试

### 9.1 全局约束

```ts
beforeAll(() => {
  vi.stubGlobal("fetch", vi.fn(() => { throw new Error("单元测试禁止网络"); }));
});
```

**单元测试层禁止真实网络**——这是很好的硬约束，任何漏 mock 的请求会立刻炸而不是静默超时。

### 9.2 单元测试（10 个文件，`tests/unit/` 镜像 `src/` 结构）

| 文件                                              | 覆盖内容                                                         | 强度 |
| ------------------------------------------------- | ---------------------------------------------------------------- | ---- |
| `api/client.test.ts`（88 行）                     | `apiFetch` 返回信封、baseURL 拼接、非 2xx 抛错                   | 中   |
| `api/index.test.ts`（19 行）                      | zod schema 能解析标准信封、`getHealthz` 是函数                   | 弱   |
| `App.test.ts`（13 行）                            | 只断言 `wrapper.exists()`                                        | 极弱 |
| `features/health/constants.test.ts`（34 行）      | `parseHeartbeatInterval` 5 个分支                                | 强   |
| `features/health/useHealthCheck.test.ts`（91 行） | 合法响应通过、非法响应丢弃并 warn、数据未就绪不校验              | 中   |
| `lib/logger.test.ts`（45 行）                     | 脱敏 `token → "***"`、`configure` 写级别、`configureLogger` 不抛 | 中   |
| `lib/storage.test.ts`（76 行）                    | `parseState` 4 例、`migrate` 3 例、`loadState`/`saveState` 往返  | 强   |
| `router/router.test.ts`（28 行）                  | 路由表形状（纯结构断言）                                         | 弱   |
| `stores/app.test.ts`（24 行）                     | 只断言 store 可创建                                              | 极弱 |

**mock 手法**：`useHealthCheck.test.ts` 用 `vi.mock(import("@/api"), ...)` 部分替换（保留 `actual` 的
`Healthz200Response`，只换 `useGetHealthz`），并用 `vi.hoisted` 提升可变状态对象；`logger.test.ts` 整体 mock `consola`
的 `createConsola`。

### 9.3 e2e（1 个文件）

```ts
test("首页可访问", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/应用/u);
});
```

**只验标题**。不验状态指示灯、不验 `/healthz` 请求、不验路由重定向。

### 9.4 覆盖缺口

* `client.ts` 的 `parseBody` 分支：204/205 空体、`blob()`、纯文本、无 content-type 全部未测
* `useHealthCheck` 的 `status`/`online` 推导与轮询参数（`enabled`/`refetchInterval`/`retry`）未测
* `stores/app.ts` 的 `serializer` 往返未测
* `router` 无守卫可测，`meta.title` 无消费方
* `App.test.ts` 挂载含 `<RouterView />` 的 App 但**未安装 router 插件**，Vue 会打 "Failed to resolve component"
  警告，测试只断言 `exists()` 所以照样通过——**测试通过不代表组件可渲染**

## 10. 关键文件

| 文件                                                                                                           | 作用                        |
| -------------------------------------------------------------------------------------------------------------- | --------------------------- |
| [main.ts](../apps/web/src/main.ts)                                                                             | 入口与插件装配              |
| [api/client.ts](../apps/web/src/api/client.ts)                                                                 | fetch 封装（orval mutator） |
| [lib/storage.ts](../apps/web/src/lib/storage.ts)                                                               | 版本化持久化管线            |
| [lib/logger.ts](../apps/web/src/lib/logger.ts)                                                                 | 结构化日志与脱敏            |
| [features/health/composables/useHealthCheck.ts](../apps/web/src/features/health/composables/useHealthCheck.ts) | 存活轮询与契约校验          |
| [router/routes.ts](../apps/web/src/router/routes.ts)                                                           | 路由表                      |
| [vite.config.ts](../apps/web/vite.config.ts)                                                                   | 构建与测试配置              |
| [orval.config.ts](../apps/web/orval.config.ts)                                                                 | 客户端生成配置              |
