/** 日志配置 */
import { configure } from "@app/log";

/** 配置日志级别 */
export const configureLogger = (): void => {
  // 日志级别
  configure(3);
};
