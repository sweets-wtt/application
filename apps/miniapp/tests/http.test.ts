/** HTTP 请求测试 */
import { describe, expect, it, vi } from "vitest";
import { appFetch } from "@/adapters/http";

describe("http", () => {
  it("方法大写并拼接基础地址", async () => {
    // 请求桩
    const request = vi.fn(async (_options?: unknown) => ({
      statusCode: 200,
      data: { ok: true },
    }));

    vi.stubGlobal("uni", { request });

    const result = await appFetch<{ ok: boolean }>("/healthz", {
      method: "get",
    });
    const options = request.mock.calls[0]?.[0];

    expect(options).toMatchObject({ url: "/healthz", method: "GET" });
    expect(result).toEqual({ ok: true });
  });

  it("非 2xx 抛错", async () => {
    vi.stubGlobal("uni", {
      request: vi.fn(async () => ({ statusCode: 500, data: {} })),
    });

    await expect(appFetch("/healthz")).rejects.toThrow("500");
  });
});
