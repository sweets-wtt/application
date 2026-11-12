import { describe, expect, it, vi } from "vitest";

import { configure, configureLogger, logger } from "@/lib/logger";

import type { ConsolaInstance } from "consola";

/** 日志级别：warn */
const LEVEL_WARN = 4;

/** 模拟 Consola 实例：仅覆盖日志器用到的成员 */
const instance = vi.hoisted(() => ({
  error: vi.fn<(message: string, data?: Readonly<Record<string, unknown>>) => void>(),
  info: vi.fn<(message: string, data?: Readonly<Record<string, unknown>>) => void>(),
  level: 3,
  warn: vi.fn<(message: string, data?: Readonly<Record<string, unknown>>) => void>(),
}));

vi.mock(import("consola"), () => ({
  // 模块模拟边界：模拟实例不含 Consola 完整成员，断言不可避免
  // eslint-disable-next-line typescript/no-unsafe-type-assertion
  createConsola: (): ConsolaInstance => instance as unknown as ConsolaInstance,
}));

describe("logger()", () => {
  it("info 输出脱敏数据", () => {
    // 敏感键应被掩码
    logger.info("hello", { token: "x", user: "app" });

    expect(instance.info).toHaveBeenCalledWith("hello", { token: "***", user: "app" });
  });

  it("configure 配置级别", () => {
    // 级别写入实例
    configure(LEVEL_WARN);

    expect(instance.level).toBe(LEVEL_WARN);
  });

  it("configureLogger 不抛错", () => {
    // 默认配置不应抛出
    expect(() => {
      configureLogger();
    }).not.toThrow();
  });
});
