/** API 基地址（默认同源相对路径） */
let baseUrl = "";

/** 设置 API 基地址：需在首次请求前调用 */
export const setBaseUrl = (value: string): void => {
  baseUrl = value;
};

/** 读取当前 API 基地址 */
export const getBaseUrl = (): string => baseUrl;

/** 无响应体：204 No Content */
const STATUS_NO_CONTENT = 204;

/** 无响应体：205 Reset Content */
const STATUS_RESET_CONTENT = 205;

/** 无响应体的状态码集合 */
const EMPTY_BODY_STATUS = new Set([STATUS_NO_CONTENT, STATUS_RESET_CONTENT]);

/** 无响应体状态 */
const hasEmptyBody = (response: Response): boolean => EMPTY_BODY_STATUS.has(response.status);

/** 文本响应：空串视为无响应体，否则尝试按 JSON 解析 */
const parseText = (text: string): unknown => {
  if (text === "") {
    return undefined;
  }

  try {
    return JSON.parse(text) as unknown;
  } catch {
    return text;
  }
};

/** 按响应类型解析响应体 */
const parseBody = async (response: Response): Promise<unknown> => {
  if (hasEmptyBody(response)) {
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

  // 文本或无 content-type
  return parseText(await response.text());
};

/** 应用 fetch 客户端：返回 Orval 约定的 { data, status, headers } */
export const apiFetch = async <TData>(path: string, init?: RequestInit): Promise<TData> => {
  const response = await fetch(`${baseUrl}${path}`, init);

  // 非 2xx 响应
  if (!response.ok) {
    throw new Error(`${response.status} ${path}`);
  }

  return {
    data: await parseBody(response),
    headers: response.headers,
    status: response.status,
  } as TData;
};
