/** 路由实例 */
import { createRouter, createWebHistory } from "vue-router";
import { routes } from "@/router/routes";
import { setupGuards } from "@/router/guards";

// 创建路由
export const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 注册守卫
setupGuards(router);
