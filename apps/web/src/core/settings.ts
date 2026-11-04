/** 应用配置：集中环境变量与运行时常量 */

// 心跳默认间隔（毫秒）
export const DEFAULT_HEARTBEAT_INTERVAL = 30_000;

/**
 * 解析心跳间隔：空串、非数字与非正值一律回退默认
 *
 * 构建时注入空值（`VITE_HEARTBEAT_INTERVAL=`）会得到空串，
 * 直接 Number 转换会退化为 0，导致轮询被静默关闭。
 */
export const parseHeartbeatInterval = (raw?: string): number => {
  const value = Number(raw);

  return Number.isFinite(value) && value > 0 ? value : DEFAULT_HEARTBEAT_INTERVAL;
};

// API 基地址（未注入则走同源相对路径）
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

// 心跳轮询间隔（毫秒）
export const HEARTBEAT_INTERVAL = parseHeartbeatInterval(import.meta.env.VITE_HEARTBEAT_INTERVAL);
