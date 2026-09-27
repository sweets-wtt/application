/** 应用配置：集中环境变量与运行时常量 */

// API 基地址（未注入则走同源相对路径）
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

// 发布版本（应用 tag）
export const RELEASE = import.meta.env.VITE_RELEASE ?? "local";

// 遥测上报端点（未注入则关闭上报）
export const TELEMETRY_URL = import.meta.env.VITE_TELEMETRY_URL ?? "";

// 心跳轮询间隔（毫秒）
export const HEARTBEAT_INTERVAL = Number(
  import.meta.env.VITE_HEARTBEAT_INTERVAL ?? 30_000,
);
