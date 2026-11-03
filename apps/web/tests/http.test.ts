/** 契约客户端测试 */
import { afterEach, describe, expect, it, vi } from "vitest";
import { appFetch, setBaseUrl } from "@/contracts";

// 每个用例后恢复基地址
afterEach(() => {
  setBaseUrl("");
});

describe("appFetch", () => {
  it("返回 Orval 约定的 data/status/headers", async () => {
    const body = { code: 0, message: "ok", data: { status: "ok" } };
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(body), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await appFetch<{ data: typeof body; status: number; headers: Headers }>(
      "/healthz",
    );

    expect(result.data).toEqual(body);
    expect(result.status).toBe(200);
    expect(result.headers.get("content-type")).toContain("application/json");
    expect(fetchMock).toHaveBeenCalledWith("/healthz", undefined);
  });

  it("拼接基地址", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ code: 0 }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);
    setBaseUrl("https://api.example.com");

    await appFetch("/healthz");

    expect(fetchMock).toHaveBeenCalledWith("https://api.example.com/healthz", undefined);
  });

  it("非 2xx 抛错", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "fail" }), {
          status: 500,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    await expect(appFetch("/healthz")).rejects.toThrow("500");
  });
});
