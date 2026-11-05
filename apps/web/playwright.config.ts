import { defineConfig } from "@playwright/test";

export default defineConfig({
  retries: 0,
  testDir: "./tests/e2e",
  use: { screenshot: "off", trace: "off", video: "off" },
  webServer: { command: "bun run preview", port: 4173, reuseExistingServer: !process.env.CI },
});
