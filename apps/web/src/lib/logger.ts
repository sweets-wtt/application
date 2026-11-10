import { createConsola } from "consola";

import type { ConsolaInstance } from "consola";

/** 敏感值掩码 */
const MASK = "***";

/** 日志级别：silent */
const LOG_LEVEL_SILENT = 0;

/** 日志级别：fatal */
const LOG_LEVEL_FATAL = 1;

/** 日志级别：trace */
const LOG_LEVEL_TRACE = 2;

/** 日志级别：info */
const LOG_LEVEL_INFO = 3;

/** 日志级别：warn */
const LOG_LEVEL_WARN = 4;

/** 日志级别：error */
const LOG_LEVEL_ERROR = 5;

/** 默认日志级别：info */
const DEFAULT_LOG_LEVEL = LOG_LEVEL_INFO;

/** 敏感键 */
const SENSITIVE_KEYS = new Set(["password", "secret", "token", "authorization", "api_key"]);

/** 可用日志级别 */
type LogLevel =
  | typeof LOG_LEVEL_SILENT
  | typeof LOG_LEVEL_FATAL
  | typeof LOG_LEVEL_TRACE
  | typeof LOG_LEVEL_INFO
  | typeof LOG_LEVEL_WARN
  | typeof LOG_LEVEL_ERROR;

/**
 * 按键脱敏单个字段
 *
 * @param {string} key 字段名
 * @param {unknown} value 字段值
 * @returns {unknown} 脱敏后的值
 */
const maskValue = (key: string, value: unknown): unknown => {
  if (SENSITIVE_KEYS.has(key.toLowerCase())) {
    return MASK;
  }

  return value;
};

/**
 * 数据脱敏
 *
 * @param {Record<string, unknown>} data 待脱敏的数据
 * @returns {Record<string, unknown>} 脱敏后的数据
 */
const redact = (data: Readonly<Record<string, unknown>> = {}): Record<string, unknown> => {
  const masked: Record<string, unknown> = {};

  // 逐字段按键名脱敏
  for (const [key, value] of Object.entries(data)) {
    masked[key] = maskValue(key, value);
  }

  return masked;
};

/**
 * 创建 Consola 实例：无 console 环境返回 undefined
 *
 * @returns {ConsolaInstance | undefined} 日志实例
 */
const createInstance = (): ConsolaInstance | undefined => {
  // 以可选视图访问 console：部分运行时环境不提供 console
  const host = globalThis as { readonly console?: Console };

  if (host.console === undefined) {
    return undefined;
  }

  return createConsola({ level: DEFAULT_LOG_LEVEL });
};

/** 多端实例：无 console 环境降级为空实现 */
const instance = createInstance();

/** 结构化日志器：应用不直接依赖 Consola */
export const logger = {
  /**
   * 输出错误日志
   *
   * @param {string} message 日志消息
   * @param {Record<string, unknown>} [data] 附加数据
   */
  error: (message: string, data?: Readonly<Record<string, unknown>>): void => {
    instance?.error(message, redact(data));
  },
  /**
   * 输出信息日志
   *
   * @param {string} message 日志消息
   * @param {Record<string, unknown>} [data] 附加数据
   */
  info: (message: string, data?: Readonly<Record<string, unknown>>): void => {
    instance?.info(message, redact(data));
  },
  /**
   * 输出警告日志
   *
   * @param {string} message 日志消息
   * @param {Record<string, unknown>} [data] 附加数据
   */
  warn: (message: string, data?: Readonly<Record<string, unknown>>): void => {
    instance?.warn(message, redact(data));
  },
};

/**
 * 配置日志级别
 *
 * @param {LogLevel} level 日志级别
 */
export const configure = (level: LogLevel): void => {
  if (instance) {
    instance.level = level;
  }
};

/** 配置日志：默认 info 级别 */
export const configureLogger = (): void => {
  configure(DEFAULT_LOG_LEVEL);
};
