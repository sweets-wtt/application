/** 心跳默认间隔（毫秒） */
export const DEFAULT_HEARTBEAT_INTERVAL = 30_000;

/** 间隔下限（毫秒）：非正值视为无效 */
const MIN_INTERVAL = 0;

/**
 * 解析心跳间隔：空串、非数字与非正值一律回退默认
 *
 * 构建时注入空值（`VITE_HEARTBEAT_INTERVAL=`）会得到空串，
 * 直接 Number 转换会退化为 0，导致轮询被静默关闭
 *
 * @param {string} [raw] 环境变量注入的原始字符串
 * @returns {number} 合法的轮询间隔（毫秒）
 */
export const parseHeartbeatInterval = (raw?: string): number => {
  const value = Number(raw);

  // 非有限数或非正值回退默认
  if (!Number.isFinite(value) || value <= MIN_INTERVAL) {
    return DEFAULT_HEARTBEAT_INTERVAL;
  }

  return value;
};

/** 心跳轮询间隔（毫秒） */
export const HEARTBEAT_INTERVAL = parseHeartbeatInterval(import.meta.env.VITE_HEARTBEAT_INTERVAL);

/** 服务端状态值 */
export const SERVER_STATUS = {
  /** 检测中 */
  checking: "checking",
  /** 离线 */
  offline: "offline",
  /** 在线 */
  online: "online",
} as const;

/** 服务端状态 */
export type ServerStatus = (typeof SERVER_STATUS)[keyof typeof SERVER_STATUS];
