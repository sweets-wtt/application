/** Playwright - https://playwright.dev/docs/test-configuration */
import { defineConfig } from "@playwright/test";

export default defineConfig({
  // 测试目录
  testDir: "./tests/e2e",

  // 失败重试
  retries: 0,

  // 报告器
  reporter: "line",

  // 浏览器选项
  use: {
    // 跟踪
    trace: "off",
    // 录像
    video: "off",
    // 截图
    screenshot: "off",
  },

  // 开发服务器
  webServer: {
    // 启动命令
    command: "vite preview --port 4173",
    // 端口
    port: 4173,
  },
});
