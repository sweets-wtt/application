import { type ConsolaInstance, createConsola } from "consola";

/** 敏感值掩码 */
const MASK = "***";

/** 日志级别：info */
const LOG_LEVEL_INFO = 3;

/** 日志级别：warn */
const LOG_LEVEL_WARN = 4;

/** 日志级别：error */
const LOG_LEVEL_ERROR = 5;

/** 敏感键 */
const SENSITIVE_KEYS = new Set(["password", "secret", "token", "authorization", "api_key"]);

/** 可用日志级别 */
type LogLevel = 0 | 1 | 2 | typeof LOG_LEVEL_INFO | typeof LOG_LEVEL_WARN | typeof LOG_LEVEL_ERROR;

/** 按键脱敏单个字段 */
const maskValue = (key: string, value: unknown): unknown => {
  if (SENSITIVE_KEYS.has(key.toLowerCase())) {
    return MASK;
  }

  return value;
};

/** 数据脱敏 */
const redact = (data: Record<string, unknown> = {}): Record<string, unknown> =>
  Object.fromEntries(Object.entries(data).map(([key, value]) => [key, maskValue(key, value)]));

/** 创建 Consola 实例：无 console 环境返回 undefined */
const createInstance = (): ConsolaInstance | undefined => {
  if (globalThis.console === undefined) {
    return;
  }

  return createConsola({ level: LOG_LEVEL_INFO });
};

/** 多端实例：无 console 环境降级为空实现 */
const instance = createInstance();

/** 结构化日志器：应用不直接依赖 Consola */
export const logger = {
  /** 输出错误日志 */
  error: (message: string, data?: Record<string, unknown>): void => {
    instance?.error(message, redact(data));
  },
  /** 输出信息日志 */
  info: (message: string, data?: Record<string, unknown>): void => {
    instance?.info(message, redact(data));
  },
  /** 输出警告日志 */
  warn: (message: string, data?: Record<string, unknown>): void => {
    instance?.warn(message, redact(data));
  },
};

/** 配置日志级别 */
export const configure = (level: LogLevel): void => {
  if (instance) {
    instance.level = level;
  }
};

/** 配置日志：默认 info 级别 */
export const configureLogger = (): void => {
  configure(LOG_LEVEL_INFO);
};
