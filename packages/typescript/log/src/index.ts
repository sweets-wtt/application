/** 结构化日志 */
import { type ConsolaInstance, createConsola } from "consola";

// 敏感键
const SENSITIVE_KEYS = new Set(["password", "secret", "token", "authorization", "api_key"]);

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
  },
};

/** 配置日志级别 */
export const configure = (level: 0 | 1 | 2 | 3 | 4 | 5): void => {
  if (instance) {
    instance.level = level;
  }
};

// 上报事件
export interface ReportEvent {
  // 指纹
  fingerprint: string;
  // 消息
  message: string;
  // 发布版本
  release?: string;
}

// 上报配置（未注入发送函数则上报关闭）
let reporting:
  | {
      // 上报端点
      endpoint: string;
      // 发送函数
      send: (endpoint: string, events: ReportEvent[]) => void;
    }
  | undefined;

// 发布版本
let appRelease: string | undefined;

// 批量缓冲
const buffer: ReportEvent[] = [];

// 批量间隔（毫秒）
const FLUSH_INTERVAL = 5_000;

// 批量定时器
let flushTimer: ReturnType<typeof setTimeout> | undefined;

/** 生成异常指纹 */
const fingerprint = (error: unknown): string => {
  if (error instanceof Error) {
    return `${error.name}:${error.message}`;
  }
  return `Unknown:${String(error)}`;
};

/** 静默批量上报：失败丢弃，不重试 */
const flush = (): void => {
  if (reporting === undefined || buffer.length === 0) {
    return;
  }
  const events = buffer.splice(0, buffer.length);
  try {
    reporting.send(reporting.endpoint, events);
  } catch {
    // 静默丢弃
  }
};

/** 调度批量上报 */
const schedule = (): void => {
  if (flushTimer !== undefined) {
    return;
  }
  flushTimer = setTimeout(() => {
    flushTimer = undefined;
    flush();
  }, FLUSH_INTERVAL);
};

/** 设置上报配置：未注入发送函数则上报关闭 */
export const setReporting = (
  config:
    | {
        // 上报端点
        endpoint: string;
        // 发送函数
        send: (endpoint: string, events: ReportEvent[]) => void;
      }
    | undefined,
): void => {
  reporting =
    config?.send === undefined ? undefined : { endpoint: config.endpoint, send: config.send };
  if (reporting === undefined) {
    buffer.length = 0;
  }
};

/** 设置发布版本 */
export const setRelease = (value: string): void => {
  appRelease = value;
};

/** 捕获异常：生成指纹、error 级日志并入上报队列 */
export const captureError = (error: unknown): string => {
  const mark = fingerprint(error);
  const message = error instanceof Error ? error.message : String(error);
  logger.error(mark, { message });
  if (reporting !== undefined) {
    buffer.push({ fingerprint: mark, message, release: appRelease });
    schedule();
  }
  return mark;
};
