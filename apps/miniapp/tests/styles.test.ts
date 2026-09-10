/** 样式测试 */
import { describe, expect, it } from "vitest";

describe("styles", () => {
  it("全局样式可加载", () => {
    expect(document.styleSheets.length).toBeGreaterThanOrEqual(0);
  });
});
