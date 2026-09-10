/** 应用入口 */
import "virtual:uno.css";

import { createSSRApp } from "vue";

import App from "./App.vue";
import { queryClient, VueQueryPlugin } from "./core/query";
import { Pinia, pinia } from "./stores";

// 创建应用
export function createApp() {
  const app = createSSRApp(App);

  // 状态管理
  app.use(pinia);

  // HTTP 查询
  app.use(VueQueryPlugin, { queryClient });

  return { app, Pinia };
}
