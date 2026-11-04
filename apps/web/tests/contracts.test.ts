import { expect, it } from "vitest";
import { Healthz200Response, getHealthz } from "../src/contracts";

it("zod 模式解析标准响应", () => {
  expect(Healthz200Response.parse({ code: 0, message: "ok", data: { status: "ok" } })).toEqual({
    code: 0,
    message: "ok",
    data: { status: "ok" },
  });
});

it("客户端函数存在", () => {
  expect(typeof getHealthz).toBe("function");
});
