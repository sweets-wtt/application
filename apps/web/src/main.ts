/** 应用入口 */
import "virtual:uno.css";
import "./core/logger";
import "./styles/main.css";

import { VueQueryPlugin } from "@tanstack/vue-query";
import { createApp } from "vue";

import App from "./App.vue";
import { queryClient } from "./core/query";
import { router } from "./router";
import { pinia } from "./stores";

const app = createApp(App);

// 状态管理
app.use(pinia);

// 路由
app.use(router);

// HTTP 查询
app.use(VueQueryPlugin, { queryClient });

app.mount("#app");
