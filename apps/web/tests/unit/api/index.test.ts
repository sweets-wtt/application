import { expect, test } from "vitest";

import { Healthz200Response, getHealthz } from "@/api";

test("zod 模式解析标准响应", () => {
  expect(
    Healthz200Response.parse({ code: 0, data: { status: "ok" }, message: "ok" }),
  ).toStrictEqual({ code: 0, data: { status: "ok" }, message: "ok" });
});

test("客户端函数存在", () => {
  expect(getHealthz).toBeTypeOf("function");
});
