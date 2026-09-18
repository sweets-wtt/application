/** 日志测试 */
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { captureError, configure, logger, setRelease } from "../src/index";

// 首次上报的请求体
const firstSend = (send: ReturnType<typeof vi.fn>): string => {
  const body = send.mock.calls[0]?.[0];
  if (typeof body !== "string") {
    throw new Error("未上报");
  }
  return body;
};

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
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
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

it("未注入发送函数时上报关闭", async () => {
  configure(3);
  setRelease("v1.0.0");
  logger.error("boom");
  captureError(new Error("bang"));
  await vi.advanceTimersByTimeAsync(5000);

  // 无通道时事件不入队 配置通道后亦无历史事件可发
  const send = vi.fn();
  configure(3, { send });
  logger.error("after");
  await vi.advanceTimersByTimeAsync(5000);

  expect(send).toHaveBeenCalledTimes(1);
  const payload = JSON.parse(firstSend(send));
  expect(payload.events).toHaveLength(1);
  expect(payload.events[0].message).toBe("after");
});

it("批量上报携带版本号 指纹与脱敏", async () => {
  const send = vi.fn();
  configure(3, { send });
  setRelease("v1.2.3");
  logger.error("boom", { token: "x" });
  captureError(new Error("bang"));
  await vi.advanceTimersByTimeAsync(5000);

  expect(send).toHaveBeenCalledTimes(1);
  const payload = JSON.parse(firstSend(send));
  expect(payload.release).toBe("v1.2.3");
  expect(payload.events).toHaveLength(2);
  expect(payload.events[0].data.token).toBe("***");
  expect(payload.events[0].fingerprint).toMatch(/^[0-9a-f]{8}$/);
  expect(payload.events[1].fingerprint).toMatch(/^[0-9a-f]{8}$/);
  expect(payload.events[0].fingerprint).not.toBe(payload.events[1].fingerprint);
});

it("发送失败静默丢弃 不重试", async () => {
  const send = vi.fn(() => Promise.reject(new Error("网络不可用")));
  configure(3, { send });
  logger.error("boom");
  await vi.advanceTimersByTimeAsync(5000);

  expect(send).toHaveBeenCalledTimes(1);
});

it("队列满丢弃最旧", async () => {
  const send = vi.fn();
  configure(3, { send });
  for (let index = 0; index < 120; index += 1) {
    logger.error(`m${index}`);
  }
  await vi.advanceTimersByTimeAsync(5000);

  const payload = JSON.parse(firstSend(send));
  expect(payload.events).toHaveLength(100);
  expect(payload.events[0].message).toBe("m20");
});

it("captureError 相同异常指纹相同", async () => {
  const send = vi.fn();
  configure(3, { send });
  captureError(new Error("same"));
  captureError(new Error("same"));
  await vi.advanceTimersByTimeAsync(5000);

  const payload = JSON.parse(firstSend(send));
  expect(payload.events[0].fingerprint).toBe(payload.events[1].fingerprint);
});
