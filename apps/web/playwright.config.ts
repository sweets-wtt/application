import { defineConfig } from "@playwright/test";
import { isCI } from "std-env";

export default defineConfig({
  retries: 0,
  testDir: "./tests/e2e",
  use: { screenshot: "off", trace: "off", video: "off" },
  // 预览服务
  webServer: { command: "bun run preview", port: 4173, reuseExistingServer: !isCI },
});
