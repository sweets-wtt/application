/** 结构化日志 */
import { type ConsolaInstance, createConsola } from "consola";

// 敏感键
const SENSITIVE_KEYS = new Set(["password", "secret", "token", "authorization", "api_key"]);

// 上报队列上限
const REPORT_QUEUE_MAX = 100;

// 上报间隔毫秒
const REPORT_INTERVAL = 5000;

/** 发送函数 由应用注入 自含端点与传输 */
export type SendFn = (body: string) => Promise<void> | void;

/** 上报事件 */
interface ReportEvent {
  level: "error";
  fingerprint: string;
  message: string;
  timestamp: string;
  data?: Record<string, unknown> | undefined;
}

/** 数据脱敏 */
const redact = (data: Record<string, unknown> = {}): Record<string, unknown> =>
  Object.fromEntries(
    Object.entries(data).map(([key, value]) => [
      key,
      SENSITIVE_KEYS.has(key.toLowerCase()) ? "***" : value,
    ]),
  );

/** 多端实例：无 console 环境降级为空实现 */
const instance: ConsolaInstance | undefined =
  typeof globalThis.console === "undefined" ? undefined : createConsola({ level: 3 });

// 上报通道 未注入则上报关闭
let reportChannel: { send: SendFn } | null = null;

// 上报版本号
let release = "";

// 上报队列
const reportQueue: ReportEvent[] = [];

// 上报定时器
let reportTimer: ReturnType<typeof setTimeout> | null = null;

/** 指纹 FNV-1a 十六进制 */
const fingerprint = (input: string): string => {
  let hash = 0x811c9dc5;
  for (let index = 0; index < input.length; index += 1) {
    hash ^= input.charCodeAt(index);
    hash = Math.imul(hash, 0x01000193);
  }
  return (hash >>> 0).toString(16).padStart(8, "0");
};

/** 批量上报 失败静默丢弃 不重试 */
const flushReport = (): void => {
  reportTimer = null;
  if (reportChannel === null || reportQueue.length === 0) {
    return;
  }
  const batch = reportQueue.splice(0, reportQueue.length);
  Promise.resolve()
    .then(() => reportChannel?.send(JSON.stringify({ release, events: batch })))
    .catch(() => undefined);
};

/** 入队 满丢最旧 并调度冲刷 */
const enqueue = (event: ReportEvent): void => {
  if (reportChannel === null) {
    return;
  }
  if (reportQueue.length >= REPORT_QUEUE_MAX) {
    reportQueue.shift();
  }
  reportQueue.push(event);
  if (reportTimer === null) {
    reportTimer = setTimeout(flushReport, REPORT_INTERVAL);
  }
};

/** 结构化日志器：应用不直接依赖 Consola */
export const logger = {
  info: (message: string, data?: Record<string, unknown>): void => {
    instance?.info(message, redact(data));
  },
  warn: (message: string, data?: Record<string, unknown>): void => {
    instance?.warn(message, redact(data));
  },
  error: (message: string, data?: Record<string, unknown>): void => {
    instance?.error(message, redact(data));
    enqueue({
      level: "error",
      fingerprint: fingerprint(`Error:${message}`),
      message,
      timestamp: new Date().toISOString(),
      data: data === undefined ? undefined : redact(data),
    });
  },
};

/** 配置日志级别与上报通道 未注入发送函数则上报关闭 */
export const configure = (
  level: 0 | 1 | 2 | 3 | 4 | 5,
  channel?: { send: SendFn } | null,
): void => {
  if (instance) {
    instance.level = level;
  }
  reportChannel = channel ?? null;
};

/** 记录版本号 */
export const setRelease = (value: string): void => {
  release = value;
};

/** 捕获异常 生成指纹并入队 */
export const captureError = (error: unknown, data?: Record<string, unknown>): void => {
  const name = error instanceof Error ? error.name : "Error";
  const message = error instanceof Error ? error.message : String(error);
  enqueue({
    level: "error",
    fingerprint: fingerprint(`${name}:${message}`),
    message,
    timestamp: new Date().toISOString(),
    data: data === undefined ? undefined : redact(data),
  });
};
