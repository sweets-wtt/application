/** UI 测试 */
import { describe, expect, it } from "vitest";

describe("ui", () => {
  it("UI 组件库可导入", async () => {
    const mod = await import("reka-ui");

    expect(mod.DialogRoot).toBeDefined();
  });
});
