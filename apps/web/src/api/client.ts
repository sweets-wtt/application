/** API 基地址（默认同源相对路径） */
let baseUrl = "";

/** 设置 API 基地址：需在首次请求前调用 */
export const setBaseUrl = (value: string): void => {
  baseUrl = value;
};

/** 读取当前 API 基地址 */
export const getBaseUrl = (): string => baseUrl;

/** 按响应类型解析响应体 */
const parseBody = async (response: Response): Promise<unknown> => {
  // 204/205 无响应体
  if (response.status === 204 || response.status === 205) {
    return undefined;
  }

  const contentType = response.headers.get("content-type") ?? "";

  // JSON 响应
  if (contentType.includes("application/json")) {
    return response.json();
  }

  // 二进制响应
  if (contentType !== "" && !contentType.startsWith("text/")) {
    return response.blob();
  }

  // 文本或无 content-type：读取文本后尝试 JSON
  const text = await response.text();

  if (text === "") {
    return undefined;
  }

  try {
    return JSON.parse(text) as unknown;
  } catch {
    return text;
  }
};

/** 应用 fetch 客户端：返回 Orval 约定的 { data, status, headers } */
export const apiFetch = async <T>(url: string, init?: RequestInit): Promise<T> => {
  const response = await fetch(`${baseUrl}${url}`, init);

  // 非 2xx 响应
  if (!response.ok) {
    throw new Error(`${response.status} ${url}`);
  }

  return {
    data: await parseBody(response),
    headers: response.headers,
    status: response.status,
  } as T;
};
