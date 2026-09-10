/** 路由测试 */
import { describe, expect, it } from "vitest";
import { router } from "@/router";

describe("router", () => {
  it("路由已注册", () => {
    expect(router.getRoutes().length).toBeGreaterThan(0);
  });

  it("首页路径为空字符串", () => {
    const home = router.resolve("/");
    expect(home.name).toBe("home");
  });
});
