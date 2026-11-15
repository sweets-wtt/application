/** API 基地址（默认同源相对路径） */
let baseUrl = "";

/**
 * 设置 API 基地址：需在首次请求前调用
 *
 * @param {string} value 新的基地址
 */
export const setBaseUrl = (value: string): void => {
  baseUrl = value;
};

/**
 * 读取当前 API 基地址
 *
 * @returns {string} 当前基地址
 */
export const getBaseUrl = (): string => baseUrl;

/** 无响应体：204 No Content */
const STATUS_NO_CONTENT = 204;

/** 无响应体：205 Reset Content */
const STATUS_RESET_CONTENT = 205;

/** 无响应体的状态码集合 */
const EMPTY_BODY_STATUS = new Set([STATUS_NO_CONTENT, STATUS_RESET_CONTENT]);

/**
 * 响应解析所需的只读视图：仅声明解析用到的能力
 */
export interface ResponseView {
  /** 状态码 */
  readonly status: number;
  /** 读取响应头 */
  readonly headers: { readonly get: (name: string) => string | null };
  /** 读取 JSON 响应体 */
  readonly json: () => Promise<unknown>;
  /** 读取二进制响应体 */
  readonly blob: () => Promise<Blob>;
  /** 读取文本响应体 */
  readonly text: () => Promise<string>;
}

/**
 * 判断状态码是否表示无响应体
 *
 * @param {object} response 只读状态视图
 * @param {number} response.status 状态码
 * @returns {boolean} 是否为无响应体状态码
 */
const hasEmptyBody = (response: { readonly status: number }): boolean => EMPTY_BODY_STATUS.has(response.status);

/**
 * 解析文本响应：空串视为无响应体，否则尝试按 JSON 解析
 *
 * @param {string} text 响应文本
 * @returns {unknown} 解析后的值
 */
const parseText = (text: string): unknown => {
  // 空串无内容
  if (text === "") {
    return undefined;
  }

  try {
    return JSON.parse(text) as unknown;
  } catch {
    // 非 JSON 时按纯文本返回
    return text;
  }
};

/**
 * 按响应类型解析响应体
 *
 * @param {Response} response 响应对象
 * @returns {Promise<unknown>} 解析后的响应体
 */
const parseBody = async (response: ResponseView): Promise<unknown> => {
  // 无响应体状态码
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

/**
 * 应用 fetch 客户端：返回 Orval 约定的 { data, status, headers }
 *
 * @template TData 响应数据类型：须兼容约定结构
 * @param {string} path 请求路径
 * @param {RequestInit} [init] 请求初始化参数
 * @returns {Promise<TData>} 约定的响应结构
 */
export const apiFetch = async <TData extends { data: unknown; headers: Headers; status: number }>(
  path: string,
  // 请求初始化由库定义（含 AbortSignal 等可变成员），无法只读化
  // eslint-disable-next-line typescript/prefer-readonly-parameter-types
  init?: Readonly<RequestInit>,
): Promise<TData> => {
  const response = await fetch(`${baseUrl}${path}`, init);

  // 非 2xx 响应统一抛错
  if (!response.ok) {
    throw new Error(`${response.status} ${path}`);
  }

  // Orval 泛型约定：信封结构与调用方声明的 TData 一致，此断言不可避免
  // eslint-disable-next-line typescript/no-unsafe-type-assertion
  return { data: await parseBody(response), headers: response.headers, status: response.status } as TData;
};
