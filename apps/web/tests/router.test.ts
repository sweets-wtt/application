/** 路由测试 */
import { describe, expect, it } from "vitest";
import { routes } from "../src/router/routes";

describe("routes", () => {
  it("包含首页路由", () => {
    expect(routes).toHaveLength(1);
    expect(routes[0]?.path).toBe("/");
  });

  it("根路径重定向至首页", () => {
    expect(routes[0]?.redirect).toBe("/home");
  });

  it("首页子路由路径为 home", () => {
    const home = routes[0]?.children?.[0];
    expect(home?.path).toBe("home");
  });
});
