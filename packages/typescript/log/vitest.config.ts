/** Vitest - https://vitest.dev/ */
import { defineConfig } from "vitest/config";

export default defineConfig({
  // 测试
  test: {
    // 环境准备
    setupFiles: ["./tests/setup.ts"],
  },
});
