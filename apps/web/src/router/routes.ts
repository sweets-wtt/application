import type { RouteRecordRaw } from "vue-router";

/** 路由表：本阶段仅首页嵌套于默认布局 */
const routes: RouteRecordRaw[] = [
  {
    // 根路径挂载默认布局
    path: "/",
    component: async () => await import("@/layouts/DefaultLayout.vue"),
    // 根路径重定向至首页
    redirect: "/home",
    children: [
      {
        // 首页
        path: "home",
        name: "home",
        component: async () => await import("@/views/HomeView.vue"),
        meta: {
          // 页面标题
          title: "首页",
        },
      },
    ],
  },
];

export default routes;
