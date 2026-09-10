/** Vite - https://vite.dev/config/ */

import { fileURLToPath, URL } from "node:url";
import vue from "@vitejs/plugin-vue";
import UnoCSS from "unocss/vite";
import { defineConfig } from "vite";
import { configDefaults } from "vitest/config";

export default defineConfig({
  // 插件
  plugins: [vue(), UnoCSS()],

  // 路径解析
  resolve: {
    // 路径别名
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },

  // 测试
  test: {
    // 测试环境
    environment: "jsdom",
    // 初始化文件
    setupFiles: ["./tests/setup.ts"],
    // 排除路径
    exclude: [...configDefaults.exclude, "dist/**", "tests/e2e/**"],
  },
});
