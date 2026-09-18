/** 日志接线 */
import { configure, logger, type SendFn } from "@app/log";

// 遥测端点 构建期注入 未配置则上报关闭
const endpoint = import.meta.env.VITE_TELEMETRY_URL as string | undefined;

// 发送通道 fetch 提交遥测路由
const send: SendFn = (body) => {
  void fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
  });
};

// 端点存在才注入上报通道
if (endpoint) {
  configure(3, { send });
} else {
  configure(3);
}

export { configure, logger };
