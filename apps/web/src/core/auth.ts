/** 认证状态 - Casdoor 会话由服务端 Cookie 维护 */
import { computed, readonly, ref } from "vue";
import type { AuthUser } from "@app/contracts";
import { API_BASE_URL } from "@/core/settings";

export type { AuthUser } from "@app/contracts";

/** 用户状态 */
const user = ref<AuthUser | null>(null);

/** 请求中状态 */
const loading = ref(false);

/** 并发去重 */
let pending: Promise<AuthUser | null> | null = null;

/** 拉取当前用户 - 401 视为未登录 */
const fetchMe = async (): Promise<AuthUser | null> => {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    credentials: "include",
    headers: { Accept: "application/json" },
  });

  if (response.status === 401) {
    user.value = null;
    return null;
  }

  if (!response.ok) {
    throw new Error(`认证状态查询失败: ${response.status}`);
  }

  const body = (await response.json()) as { data?: AuthUser };
  user.value = body.data ?? null;

  return user.value;
};

/** 确保已加载 - 路由守卫使用 */
export const ensureAuth = async (): Promise<AuthUser | null> => {
  if (user.value) {
    return user.value;
  }

  if (!pending) {
    loading.value = true;
    pending = fetchMe().finally(() => {
      loading.value = false;
      pending = null;
    });
  }

  return await pending;
};

/** 跳转 Casdoor 登录 */
export const login = (next: string = window.location.pathname): void => {
  const target = next.startsWith("/") ? next : "/";
  window.location.assign(`/auth/login?next=${encodeURIComponent(target)}`);
};

/** 清除会话 */
export const logout = (): void => {
  user.value = null;
  window.location.assign("/auth/logout");
};

/** 认证组合式 */
export const useAuth = () => ({
  user: readonly(user),
  loading: readonly(loading),
  isAuthenticated: computed(() => user.value !== null),
  ensureAuth,
  login,
  logout,
});
