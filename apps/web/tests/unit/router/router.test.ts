import { describe, expect, it } from "vitest";

import routes from "@/router/routes";

/** 首个元素索引 */
const FIRST_INDEX = 0;

/** 根路由数量 */
const ROOT_ROUTE_COUNT = 1;

describe("routes()", () => {
  it("包含首页路由", () => {
    // 仅一条根路由
    expect(routes).toHaveLength(ROOT_ROUTE_COUNT);
    expect(routes[FIRST_INDEX]?.path).toBe("/");
  });

  it("根路径重定向至首页", () => {
    // 根路径重定向到 home
    expect(routes[FIRST_INDEX]?.redirect).toBe("/home");
  });

  it("首页子路由路径为 home", () => {
    // 取首个根路由的子路由
    const home = routes[FIRST_INDEX]?.children?.[FIRST_INDEX];
    expect(home?.path).toBe("home");
  });
});
