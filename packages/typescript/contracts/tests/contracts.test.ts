/** 契约测试 */
import { expect, it } from "vitest";
import { Healthz200Response, healthz } from "../index";

it("zod 模式解析标准响应", () => {
  expect(Healthz200Response.parse({ code: 0, message: "ok", data: { status: "ok" } })).toEqual({
    code: 0,
    message: "ok",
    data: { status: "ok" },
  });
});

it("客户端函数存在", () => {
  expect(typeof healthz).toBe("function");
});
