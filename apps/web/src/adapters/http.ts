/** 契约客户端适配 */

/** API 基础地址 */
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

/** 应用 fetch：Orval mutator */
export async function appFetch<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${url}`, init);

  if (!response.ok) {
    throw new Error(`${response.status} ${url}`);
  }

  return (await response.json()) as T;
}
