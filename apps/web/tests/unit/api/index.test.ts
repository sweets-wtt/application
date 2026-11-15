import { describe, expect, it } from "vitest";

import { Healthz200Response, getHealthz } from "@/api";

describe("api", () => {
  it("zod 模式解析标准响应", () => {
    // 按契约 schema 校验响应信封
    expect(Healthz200Response.parse({ code: 0, data: { status: "ok" }, message: "ok" })).toStrictEqual({
      code: 0,
      data: { status: "ok" },
      message: "ok",
    });
  });

  it("客户端函数存在", () => {
    // 生成的客户端函数应可调用
    expect(getHealthz).toBeTypeOf("function");
  });
});
