import { afterEach, describe, expect, it, vi } from "vitest";

import { apiFetch, setBaseUrl } from "@/api";

// 每个用例后恢复基地址
afterEach(() => {
  setBaseUrl("");
});

describe("apiFetch", () => {
  it("返回 Orval 约定的 data/status/headers", async () => {
    const body = { code: 0, data: { status: "ok" }, message: "ok" },
      fetchMock = vi
        .fn()
        .mockResolvedValue(
          new Response(JSON.stringify(body), {
            headers: { "Content-Type": "application/json" },
            status: 200,
          }),
        );
    vi.stubGlobal("fetch", fetchMock);

    const result = await apiFetch<{ data: typeof body; status: number; headers: Headers }>(
      "/healthz",
    );

    expect(result.data).toStrictEqual(body);
    expect(result.status).toBe(200);
    expect(result.headers.get("content-type")).toContain("application/json");
    expect(fetchMock).toHaveBeenCalledWith("/healthz", undefined);
  });

  it("拼接基地址", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(
        new Response(JSON.stringify({ code: 0 }), {
          headers: { "Content-Type": "application/json" },
          status: 200,
        }),
      );
    vi.stubGlobal("fetch", fetchMock);
    setBaseUrl("https://api.example.com");

    await apiFetch("/healthz");

    expect(fetchMock).toHaveBeenCalledWith("https://api.example.com/healthz", undefined);
  });

  it("非 2xx 抛错", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          new Response(JSON.stringify({ detail: "fail" }), {
            headers: { "Content-Type": "application/json" },
            status: 500,
          }),
        ),
    );

    await expect(apiFetch("/healthz")).rejects.toThrow("500");
  });
});
