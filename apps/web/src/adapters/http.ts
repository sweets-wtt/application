/** HTTP 适配器 */
import { appFetch } from "@app/contracts";
import { API_BASE_URL } from "@/core/settings";

/** 带基地址的 fetch 实现 */
export const httpFetch = (url: string, init?: RequestInit): Promise<Response> =>
  fetch(`${API_BASE_URL}${url}`, init);

/** 应用 fetch 客户端：注入基地址 */
export const clientFetch = <T>(url: string, init?: RequestInit): Promise<T> =>
  appFetch<T>(`${API_BASE_URL}${url}`, init);
