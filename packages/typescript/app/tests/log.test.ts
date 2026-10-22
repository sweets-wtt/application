import { beforeEach, expect, it, vi } from "vitest";
import { captureError, configure, logger } from "../src/log";

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
  configure({});
});

it("info 输出脱敏数据", () => {
  logger.info("hello", { user: "app", token: "x" });

  expect(instance.info).toHaveBeenCalledWith("hello", {
    user: "app",
    token: "***",
  });
});

it("configure 配置级别", () => {
  configure({ level: 4 });

  expect(instance.level).toBe(4);
});

it("configure 配置发布版本", () => {
  const send = vi.fn();
  configure({ release: "1.2.3", telemetry: { endpoint: "https://t.example", send } });
  vi.useFakeTimers();

  try {
    captureError(new Error("boom"));
    vi.advanceTimersByTime(5_000);

    expect(send).toHaveBeenCalledWith("https://t.example", [
      { fingerprint: "Error:boom", message: "boom", release: "1.2.3" },
    ]);
  } finally {
    vi.useRealTimers();
  }
});

it("注入发送函数后批量上报", () => {
  const send = vi.fn();
  configure({ telemetry: { endpoint: "https://t.example", send } });
  vi.useFakeTimers();

  try {
    captureError(new Error("boom"));
    expect(send).not.toHaveBeenCalled();

    vi.advanceTimersByTime(5_000);
    expect(send).toHaveBeenCalledTimes(1);
  } finally {
    vi.useRealTimers();
  }
});

it("telemetry.enabled = false 显式关闭", () => {
  const send = vi.fn();
  configure({ telemetry: { endpoint: "https://t.example", send, enabled: false } });
  vi.useFakeTimers();

  try {
    captureError(new Error("boom"));
    vi.advanceTimersByTime(30_000);

    expect(send).not.toHaveBeenCalled();
  } finally {
    vi.useRealTimers();
  }
});

it("发送失败静默丢弃", () => {
  const send = vi.fn(() => {
    throw new Error("network");
  });
  configure({ telemetry: { endpoint: "https://t.example", send } });
  vi.useFakeTimers();

  try {
    captureError(new Error("boom"));

    expect(() => vi.advanceTimersByTime(5_000)).not.toThrow();
    expect(send).toHaveBeenCalledTimes(1);
  } finally {
    vi.useRealTimers();
  }
});

it("captureError 返回指纹", () => {
  expect(captureError(new Error("x"))).toBe("Error:x");
  expect(captureError("str")).toBe("Unknown:str");
});
