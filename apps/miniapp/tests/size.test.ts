/** 体积测试 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("size", () => {
  it("体积限制已配置", () => {
    const manifest = JSON.parse(readFileSync(resolve(process.cwd(), "package.json"), "utf8")) as {
      "size-limit": { path: string; limit: string }[];
    };

    expect(manifest["size-limit"][0]?.limit).toBe("2 MiB");
    expect(manifest["size-limit"][0]?.path).toBe("dist/build/mp-weixin/**/*.js");
  });
});
