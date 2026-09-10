/** 日志测试 */
import { describe, expect, it } from "vitest";
import { logger } from "@/core/logger";

describe("logger", () => {
  it("日志器可导入", () => {
    expect(typeof logger.info).toBe("function");
    expect(typeof logger.warn).toBe("function");
    expect(typeof logger.error).toBe("function");
  });
});
