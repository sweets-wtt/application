/** UI 测试 */
import { describe, expect, it } from "vitest";

describe("ui", () => {
  it("UI 组件库可解析", async () => {
    const mod = await import("wot-design-uni/components/wd-button/wd-button.vue");

    expect(mod.default).toBeDefined();
  });
});
