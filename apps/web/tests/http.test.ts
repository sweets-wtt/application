/** HTTP 适配器测试 */
import { describe, expect, it, vi } from "vitest";
import { clientFetch, httpFetch } from "../src/adapters/http";

describe("http adapter", () => {
  it("clientFetch 调用 appFetch", async () => {
    // 桩 fetch
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ code: 0 }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await clientFetch<{ code: number }>("/healthz");

    expect(result).toEqual({ code: 0 });
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/healthz"), undefined);
  });

  it("httpFetch 带基地址", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true });
    vi.stubGlobal("fetch", fetchMock);

    await httpFetch("/test");

    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/test"), undefined);
  });
});
