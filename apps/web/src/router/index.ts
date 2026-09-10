/** 路由入口 */
import { createRouter, createWebHistory } from "vue-router";

import { setupGuards } from "./guards";
import { routes } from "./routes";

// 路由实例
export const router = createRouter({
  // 历史模式
  history: createWebHistory(),
  // 路由表
  routes,
});

// 注册守卫
setupGuards(router);
