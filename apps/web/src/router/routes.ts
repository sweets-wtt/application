/** 路由配置 */
import type { RouteRecordRaw } from "vue-router";

// 路由：本阶段仅首页嵌套布局
export const routes: RouteRecordRaw[] = [
  {
    path: "/",
    // 布局
    component: () => import("@/layouts/index.vue"),
    // 根路径重定向至首页
    redirect: "/home",
    children: [
      {
        // 首页
        path: "home",
        name: "home",
        component: () => import("@/views/home/index.vue"),
        meta: {
          // 页面标题
          title: "首页",
        },
      },
    ],
  },
];
