/** 契约客户端适配 */

/** API 基础地址 */
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

/** 应用请求：uni.request 实现 Orval mutator */
export async function appFetch<T>(url: string, init?: RequestInit): Promise<T> {
  // 请求
  const response = await uni.request({
    // 地址
    url: `${BASE_URL}${url}`,
    // 方法大写
    method: (init?.method ?? "GET").toUpperCase() as "GET" | "POST" | "PUT" | "DELETE",
    // 请求头
    header: init?.headers as Record<string, string> | undefined,
    // 数据
    data: typeof init?.body === "string" ? JSON.parse(init.body) : undefined,
  });

  // 状态校验
  if (response.statusCode < 200 || response.statusCode >= 300) {
    throw new Error(`${response.statusCode} ${url}`);
  }

  return response.data as T;
}
