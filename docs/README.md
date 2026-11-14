# 仓库文档

本目录是对 `application` 仓库的结构化梳理，内容来自对源码与配置的逐行阅读，不含推测性描述。

## 一句话结论

这是一个**从更大系统裁剪而来的 monorepo 脚手架**：功能上只有「首页 +
服务端存活指示灯」一条竖切，但把**契约驱动代码生成、双端类型安全、严格质量门禁、容器化部署**整条链路都搭通并跑绿了。它的价值在工程骨架，不在业务。

## 文档索引

| 文档                                 | 内容                                                       |
| ------------------------------------ | ---------------------------------------------------------- |
| [architecture.md](./architecture.md) | 仓库形态、演进历史、顶层结构、契约驱动主线、部署拓扑       |
| [server.md](./server.md)             | `apps/server`：启动链路、分层约定、日志与异常、测试策略    |
| [web.md](./web.md)                   | `apps/web`：启动链路、api 层、lib 三件套、路由与状态、测试 |
| [tooling.md](./tooling.md)           | Taskfile 任务图、CI 流水线、Git 钩子、各工具配置要点       |
| [findings.md](./findings.md)         | 问题清单（按严重度）与改进优先级建议                       |

## 规模速览

| 区域        | tracked 文件 | 行数 |
| ----------- | ------------ | ---- |
| `.github`   | 4            | 309  |
| `apps`      | 71           | 1970 |
| `contracts` | 7            | 277  |
| `infra`     | 4            | 225  |

源码总量约 2.2k 行，143 个提交，分支 `main`（另有 `origin/test` 与 tag `archive/main-9ecf6db`）。

## 技术栈

| 层         | 选型                                                                                 |
| ---------- | ------------------------------------------------------------------------------------ |
| 环境与任务 | mise（全部工具 aqua 固定版本）、Taskfile                                             |
| 后端       | FastAPI + granian + pydantic-settings + structlog + schemathesis                     |
| 前端       | Vue 3 + Vite + vue-router + pinia + vue-query + orval + zod + UnoCSS + reka-ui       |
| 契约       | OpenAPI 3.1.2 + vacuum（校验与打包）+ oasdiff（兼容性）                              |
| 质量       | ruff + ty + oxlint + oxfmt + dprint + typos + gitleaks + trivy + actionlint + zizmor |
| 交付       | Docker 多阶段构建 + Caddy + docker compose                                           |
