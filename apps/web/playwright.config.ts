/** Playwright 配置 */
import { defineConfig } from "@playwright/test";

export default defineConfig({
  // 重试
  retries: 0,

  // 测试目录
  testDir: "./tests/e2e",

  // 使用
  use: {
    // 追踪
    trace: "off",
    // 视频
    video: "off",
    // 截图
    screenshot: "off",
  },

  // Web 服务器
  webServer: {
    command: "bun run preview",
    port: 4173,
    reuseExistingServer: !process.env.CI,
  },
});
