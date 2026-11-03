/** 应用配置：集中环境变量与运行时常量 */

// API 基地址（未注入则走同源相对路径）
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

// 心跳轮询间隔（毫秒）
export const HEARTBEAT_INTERVAL = Number(import.meta.env.VITE_HEARTBEAT_INTERVAL ?? 30_000);
