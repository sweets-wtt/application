/** 日志测试 */
import { beforeEach, expect, it, vi } from "vitest";
import { configure, logger } from "../src/index";

// 模拟 Consola
const instance = vi.hoisted(() => ({
  info: vi.fn(),
  warn: vi.fn(),
  error: vi.fn(),
  level: 3,
}));

vi.mock("consola", () => ({ createConsola: () => instance }));

beforeEach(() => {
  vi.clearAllMocks();
});

it("info 输出脱敏数据", () => {
  logger.info("hello", { user: "app", token: "x" });

  expect(instance.info).toHaveBeenCalledWith("hello", {
    user: "app",
    token: "***",
  });
});

it("configure 配置级别", () => {
  configure(4);

  expect(instance.level).toBe(4);
});
