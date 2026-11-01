/** 日志测试 */
import { beforeEach, expect, it, vi } from "vitest";
import { captureError, configure, logger, setReporting } from "../src/index";

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
  // 每例重置上报配置与缓冲
  setReporting(undefined);
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

it("captureError 上报载荷含真实级别与时间戳", () => {
  vi.useFakeTimers();
  vi.setSystemTime(1_700_000_000_000);
  const send = vi.fn();

  try {
    setReporting({ endpoint: "https://t", send });

    const mark = captureError(new Error("boom"));

    // flush 由 schedule 延迟触发
    vi.advanceTimersByTime(5_000);

    expect(mark).toBe("Error:boom");
    expect(send).toHaveBeenCalledTimes(1);
    const [endpoint, events] = send.mock.calls[0] as [string, unknown[]];
    expect(endpoint).toBe("https://t");
    expect(events).toEqual([
      expect.objectContaining({
        level: "error",
        fingerprint: "Error:boom",
        message: "boom",
        timestamp: 1_700_000_000_000,
      }),
    ]);
  } finally {
    setReporting(undefined);
    vi.useRealTimers();
  }
});
