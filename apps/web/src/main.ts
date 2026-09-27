/** 应用入口 */
import { createApp } from "vue";
import { VueQueryPlugin } from "@tanstack/vue-query";
import "virtual:uno.css";

import App from "@/App.vue";
import { router } from "@/router";
import { pinia } from "@/stores";
import { queryClient } from "@/core/query";
import { configureLogger } from "@/core/logger";
import "@/styles/main.css";

// 配置日志与遥测上报
configureLogger();

// 创建应用
const app = createApp(App);

// 状态管理（含持久化）
app.use(pinia);

// 路由
app.use(router);

// 数据查询
app.use(VueQueryPlugin, { queryClient });

// 挂载
app.mount("#app");
