/** 路由定义 */
import type { RouteRecordRaw } from "vue-router";

import Layout from "@/layouts/index.vue";

export const routes: RouteRecordRaw[] = [
  // 布局静态导入：全路由共享，随主包加载
  {
    path: "/",
    component: Layout,
    meta: { title: "应用" },
    children: [
      {
        path: "",
        name: "home",
        component: () => import("@/views/home/index.vue"),
        meta: { title: "首页" },
      },
    ],
  },
];
