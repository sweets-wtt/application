/** Vitest - https://vitest.dev/ */
import { defineConfig } from "vitest/config";

export default defineConfig({
  // 测试
  test: {
    // 线程池 - Windows 下 forks 临时目录会 EPERM
    pool: "threads",
    // 环境准备
    setupFiles: ["./tests/setup.ts"],
    // 排除构建产物
    exclude: ["**/node_modules/**", "**/dist/**"],
  },
});
