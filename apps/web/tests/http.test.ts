/** HTTP 请求测试 */
import { describe, expect, it } from "vitest";

describe("http", () => {
  it("HTTP 模块可导入", async () => {
    const mod = await import("@/adapters/http");

    expect(typeof mod.appFetch).toBe("function");
  });
});
