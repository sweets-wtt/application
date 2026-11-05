import { VueQueryPlugin } from "@tanstack/vue-query";
import { createApp } from "vue";

import { setBaseUrl } from "@/api";
import App from "@/App.vue";
import { API_BASE_URL } from "@/config/env";
import { configureLogger } from "@/lib/logger";
import { queryClient } from "@/lib/query";
import { router } from "@/router";
import { pinia } from "@/stores";

import "@/styles/main.css";
import "virtual:uno.css";

// 配置日志级别
configureLogger();

// 契约客户端基地址
setBaseUrl(API_BASE_URL);

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
