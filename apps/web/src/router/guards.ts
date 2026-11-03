/** 路由守卫 */
import type { Router } from "vue-router";
import { ensureAuth, type AuthUser } from "@/core/auth";

/** 注册路由守卫 */
export const setupGuards = (router: Router): void => {
  router.beforeEach(async (to) => {
    // 无需认证直接放行
    if (!to.meta.requiresAuth) {
      return true;
    }

    // 服务端会话校验 - 不信任本地 token
    let user: AuthUser | null = null;
    try {
      user = await ensureAuth();
    } catch {
      user = null;
    }

    if (user) {
      return true;
    }

    // 未认证跳转 Casdoor 登录
    window.location.assign(`/auth/login?next=${encodeURIComponent(to.fullPath)}`);
    return false;
  });
};
