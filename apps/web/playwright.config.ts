/** Playwright - https://playwright.dev/docs/test-configuration */
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  retries: 0,
  reporter: "line",

  // 浏览器选项
  use: {
    trace: "off",
    video: "off",
    screenshot: "off",
  },

  // 开发服务器
  webServer: {
    command: "vite preview --port 4173",
    port: 4173,
  },
});
