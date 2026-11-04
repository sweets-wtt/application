import { createRouter, createWebHistory } from "vue-router";
import { routes } from "@/router/routes";

// 创建路由
export const router = createRouter({
  history: createWebHistory(),
  routes,
});
