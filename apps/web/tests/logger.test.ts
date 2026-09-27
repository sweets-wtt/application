/** 日志测试 */
import { describe, expect, it, vi } from "vitest";
import { configureLogger } from "../src/core/logger";

describe("logger", () => {
  it("configureLogger 不抛错", () => {
    expect(() => configureLogger()).not.toThrow();
  });

  it("未注入遥测端点时上报关闭", () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    configureLogger();

    // 无端点不调用 fetch
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
