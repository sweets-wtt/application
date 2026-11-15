/** 契约测试 */
import { expect, it } from "vitest";
import { getDefaultMock, Healthz200, healthz } from "../index";

it("zod 模式解析标准响应", () => {
  expect(Healthz200.parse({ code: 0, message: "ok", data: { status: "ok" } })).toEqual({
    code: 0,
    message: "ok",
    data: { status: "ok" },
  });
});

it("MSW 钩子可用", () => {
  expect(getDefaultMock()).toHaveLength(1);
});

it("客户端函数存在", () => {
  expect(typeof healthz).toBe("function");
});
