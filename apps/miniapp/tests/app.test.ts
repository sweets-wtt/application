/** 应用测试 */
import { describe, expect, it } from "vitest";
import { createApp } from "@/main";

describe("app", () => {
  it("应用可创建", () => {
    const { app, Pinia } = createApp();

    expect(app).toBeDefined();
    expect(typeof Pinia.createPinia).toBe("function");
  });
});
