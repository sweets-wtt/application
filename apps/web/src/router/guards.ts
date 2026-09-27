/** 路由守卫 */
import type { Router } from "vue-router";
import { loadSession, authGuard } from "@app/auth";

// localStorage 适配为状态包 Storage 接口
const sessionStorage = {
  getItem: (key: string) => localStorage.getItem(key),
  setItem: (key: string, value: string) => localStorage.setItem(key, value),
};

/** 注册路由守卫 */
export const setupGuards = (router: Router): void => {
  router.beforeEach((to) => {
    // 无需认证直接放行
    if (!to.meta.requiresAuth) {
      return true;
    }

    // 认证守卫：会话合法且未过期
    const session = loadSession(sessionStorage);
    if (authGuard(session)) {
      return true;
    }

    // 未认证跳转首页
    return { name: "home" };
  });
};
