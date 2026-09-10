/** Vitest - https://vitest.dev/config/ */
import { fileURLToPath, URL } from "node:url";
import vue from "@vitejs/plugin-vue";
import UnoCSS from "unocss/vite";
import { configDefaults, defineConfig } from "vitest/config";

export default defineConfig({
  // 插件
  plugins: [UnoCSS(), vue()],

  // 路径别名
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },

  // 测试
  test: {
    environment: "jsdom",
    setupFiles: ["./tests/setup.ts"],
    exclude: [...configDefaults.exclude, "dist/**"],
  },
});
