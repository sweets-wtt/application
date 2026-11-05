import { describe, expect, it, vi } from "vitest";

import { apiFetch, setBaseUrl } from "@/api";

/** HTTP 状态码：成功 */
const STATUS_OK = 200;

/** HTTP 状态码：服务端错误 */
const STATUS_SERVER_ERROR = 500;

describe("apiFetch", () => {
  it("返回 Orval 约定的 data/status/headers", async () => {
    expect.hasAssertions();

    const body = { code: 0, data: { status: "ok" }, message: "ok" };
    const fetchMock = vi
      .fn()
      .mockResolvedValue(
        Response.json(body, { headers: { "Content-Type": "application/json" }, status: STATUS_OK }),
      );
    vi.stubGlobal("fetch", fetchMock);

    const result = await apiFetch<{ data: typeof body; status: number; headers: Headers }>(
      "/healthz",
    );

    expect(result.data).toStrictEqual(body);
    expect(result.status).toBe(STATUS_OK);
    expect(result.headers.get("content-type")).toContain("application/json");
    expect(fetchMock).toHaveBeenCalledWith("/healthz", undefined);
  });

  it("拼接基地址", async () => {
    expect.assertions(1);

    const fetchMock = vi
      .fn()
      .mockResolvedValue(
        Response.json(
          { code: 0 },
          { headers: { "Content-Type": "application/json" }, status: STATUS_OK },
        ),
      );
    vi.stubGlobal("fetch", fetchMock);
    setBaseUrl("https://api.example.com");

    await apiFetch("/healthz");

    expect(fetchMock).toHaveBeenCalledWith("https://api.example.com/healthz", undefined);

    setBaseUrl("");
  });

  it("非 2xx 抛错", async () => {
    expect.assertions(1);

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

    await expect(apiFetch("/healthz")).rejects.toThrow("500");
  });
});
