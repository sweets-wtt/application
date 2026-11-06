import { describe, expect, it } from "vitest";

import routes from "@/router/routes";

describe("routes", () => {
  it("包含首页路由", () => {
    // 仅一条根路由
    expect(routes).toHaveLength(1);
    expect(routes[0]?.path).toBe("/");
  }, 5000);

  it("根路径重定向至首页", () => {
    // 根路径重定向到 home
    expect(routes[0]?.redirect).toBe("/home");
  }, 5000);

  it("首页子路由路径为 home", () => {
    // 取首个根路由的子路由
    const home = routes[0]?.children?.[0];
    expect(home?.path).toBe("home");
  }, 5000);
});
