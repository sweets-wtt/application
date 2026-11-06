import { describe, expect, it, vi } from "vitest";

import { apiFetch, setBaseUrl } from "@/api";

/** HTTP 状态码：成功 */
const STATUS_OK = 200;

/** HTTP 状态码：服务端错误 */
const STATUS_SERVER_ERROR = 500;

describe("apiFetch", () => {
  it("返回 Orval 约定的 data/status/headers", async () => {
    expect.hasAssertions();

    // 构造 JSON 响应
    const body = { code: 0, data: { status: "ok" }, message: "ok" };
    const fetchMock = vi
      .fn<(input: RequestInfo | URL, init?: RequestInit) => Promise<Response>>()
      .mockResolvedValue(
        Response.json(body, { headers: { "Content-Type": "application/json" }, status: STATUS_OK }),
      );
    vi.stubGlobal("fetch", fetchMock);

    // 发起请求
    const result = await apiFetch<{ data: typeof body; status: number; headers: Headers }>(
      "/healthz",
    );

    // 校验返回值结构
    expect(result.data).toStrictEqual(body);
    expect(result.status).toBe(STATUS_OK);
    expect(result.headers.get("content-type")).toContain("application/json");
    expect(fetchMock).toHaveBeenCalledWith("/healthz", undefined);
  }, 5000);

  it("拼接基地址", async () => {
    expect.assertions(1);

    // 构造 JSON 响应
    const fetchMock = vi
      .fn<(input: RequestInfo | URL, init?: RequestInit) => Promise<Response>>()
      .mockResolvedValue(
        Response.json(
          { code: 0 },
          { headers: { "Content-Type": "application/json" }, status: STATUS_OK },
        ),
      );
    vi.stubGlobal("fetch", fetchMock);
    // 设置绝对基地址
    setBaseUrl("https://api.example.com");

    await apiFetch("/healthz");

    // 请求地址应带上基地址
    expect(fetchMock).toHaveBeenCalledWith("https://api.example.com/healthz", undefined);

    // 还原默认基地址
    setBaseUrl("");
  }, 5000);

  it("非 2xx 抛错", async () => {
    expect.assertions(1);

    // 构造 500 响应
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          Response.json(
            { detail: "fail" },
            { headers: { "Content-Type": "application/json" }, status: STATUS_SERVER_ERROR },
          ),
        ),
    );

    // 非 2xx 应抛出错误
    await expect(apiFetch("/healthz")).rejects.toThrow("500");
  }, 5000);
});
