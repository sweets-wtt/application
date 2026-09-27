/** 日志与遥测 */
import { configure, setRelease, setReporting, type ReportEvent } from "@app/log";
import { RELEASE, TELEMETRY_URL } from "@/core/settings";

/** 配置日志与遥测上报 */
export const configureLogger = (): void => {
  // 日志级别
  configure(3);

  // 发布版本
  setRelease(RELEASE);

  // 遥测端点未注入则上报关闭
  if (TELEMETRY_URL === "") {
    return;
  }

  // 批量上报：fetch 发送到遥测路由
  setReporting({
    endpoint: TELEMETRY_URL,
    send: (url: string, events: ReportEvent[]): void => {
      void fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(events),
      }).catch(() => {
        // 静默丢弃
      });
    },
  });
};
