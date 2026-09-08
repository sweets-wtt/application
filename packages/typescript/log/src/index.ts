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
