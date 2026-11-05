import type { RouteRecordRaw } from "vue-router";

// 路由：本阶段仅首页嵌套布局
const routes: RouteRecordRaw[] = [
  {
    path: "/",
    // 布局
    component: () => import("@/layouts/DefaultLayout.vue"),
    // 根路径重定向至首页
    redirect: "/home",
    children: [
      {
        // 首页
        path: "home",
        name: "home",
        // 页面组件
        component: () => import("@/views/HomeView.vue"),
        meta: {
          // 页面标题
          title: "首页",
        },
      },
    ],
  },
];

export default routes;
