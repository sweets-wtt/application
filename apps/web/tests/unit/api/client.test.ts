import { describe, expect, it, vi } from "vitest";

import { apiFetch, setBaseUrl } from "@/api";

import type { ResponseView } from "@/api";
import type { Mock } from "vitest";

/** HTTP 状态码：成功 */
const STATUS_OK = 200;

/** HTTP 状态码：服务端错误 */
const STATUS_SERVER_ERROR = 500;

/** JSON 响应头 */
const JSON_HEADERS = { "Content-Type": "application/json" };

/** 模拟 fetch 的签名：客户端实际仅以字符串路径调用 */
type FetchMock = Mock<(input: string) => Promise<ResponseView>>;

/**
 * 构造 JSON 响应
 *
 * @param {unknown} body 响应体
 * @param {number} status 状态码
 * @returns {Response} 响应对象
 */
const jsonResponse = (body: unknown, status: number): Response =>
  Response.json(body, { headers: JSON_HEADERS, status });

/**
 * 安装模拟 fetch
 *
 * @param {ResponseView} response 模拟返回的响应
 * @returns {FetchMock} 模拟函数
 */
const stubFetch = (response: ResponseView): FetchMock => {
  const mock = vi.fn<(input: string) => Promise<ResponseView>>().mockResolvedValue(response);

  vi.stubGlobal("fetch", mock);

  return mock;
};

describe("apiFetch", () => {
  it("返回约定结构", async () => {
    expect.hasAssertions();

    // 构造 JSON 响应
    const body = { code: 0, data: { status: "ok" }, message: "ok" };
    const fetchMock = stubFetch(jsonResponse(body, STATUS_OK));

    // 发起请求
    const result = await apiFetch<{ data: typeof body; status: number; headers: Headers }>("/healthz");

    // 校验返回值结构
    expect(result.data).toStrictEqual(body);
    expect(result.status).toBe(STATUS_OK);
    expect(result.headers.get("content-type")).toContain("application/json");
    expect(fetchMock).toHaveBeenCalledWith("/healthz", undefined);
  });

  it("拼接基地址", async () => {
    expect.hasAssertions();

    const fetchMock = stubFetch(jsonResponse({ code: 0 }, STATUS_OK));

    // 设置绝对基地址
    setBaseUrl("https://api.example.com");

    await apiFetch("/healthz");

    // 请求地址应带上基地址
    expect(fetchMock).toHaveBeenCalledWith("https://api.example.com/healthz", undefined);

    // 还原默认基地址
    setBaseUrl("");
  });

  it("非 2xx 抛错", async () => {
    expect.hasAssertions();

    // 构造 500 响应
    stubFetch(jsonResponse({ detail: "fail" }, STATUS_SERVER_ERROR));

    // 非 2xx 应抛出错误
    await expect(apiFetch("/healthz")).rejects.toThrow("500");
  });
});
