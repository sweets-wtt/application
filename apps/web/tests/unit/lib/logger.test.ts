import { describe, expect, it, vi } from "vitest";

import { configure, configureLogger, logger } from "@/lib/logger";

/** 日志级别：warn */
const LEVEL_WARN = 4;

// 模拟 Consola
const instance = vi.hoisted(() => ({ error: vi.fn(), info: vi.fn(), level: 3, warn: vi.fn() }));

vi.mock("consola", () => ({ createConsola: () => instance }));

describe("logger", () => {
  it("info 输出脱敏数据", () => {
    logger.info("hello", { token: "x", user: "app" });

    expect(instance.info).toHaveBeenCalledWith("hello", { token: "***", user: "app" });
  });

  it("configure 配置级别", () => {
    configure(LEVEL_WARN);

    expect(instance.level).toBe(LEVEL_WARN);
  });

  it("configureLogger 不抛错", () => {
    expect(() => configureLogger()).not.toThrow();
  });
});
