import { expect, test, vi } from "vitest";

import { configure, configureLogger, logger } from "@/lib/logger";

// 模拟 Consola
const instance = vi.hoisted(() => ({ error: vi.fn(), info: vi.fn(), level: 3, warn: vi.fn() }));

vi.mock("consola", () => ({ createConsola: () => instance }));

test("info 输出脱敏数据", () => {
  logger.info("hello", { token: "x", user: "app" });

  expect(instance.info).toHaveBeenCalledWith("hello", { token: "***", user: "app" });
});

test("configure 配置级别", () => {
  configure(4);

  expect(instance.level).toBe(4);
});

test("configureLogger 不抛错", () => {
  expect(() => configureLogger()).not.toThrow();
});
