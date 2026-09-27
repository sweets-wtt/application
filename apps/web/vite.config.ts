/** Vite - https://vite.dev/ */
import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import UnoCSS from "unocss/vite";
import Components from "unplugin-vue-components/vite";
import Icons from "unplugin-icons/vite";
import IconsResolver from "unplugin-icons/resolver";
import RekaResolver from "reka-ui/resolver";

export default defineConfig({
  // 插件
  plugins: [
    // Vue 单文件组件
    vue(),
    // 原子样式
    UnoCSS(),
    // 自动导入组件
    Components({
      resolvers: [
        // 图标组件
        IconsResolver({ prefix: "icon" }),
        // Reka UI 组件
        RekaResolver(),
      ],
    }),
    // 图标
    Icons({ autoInstall: false }),
  ],

  // 路径别名
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },

  // 测试
  test: {
    // 环境
    environment: "jsdom",
    // 准备文件
    setupFiles: ["./tests/setup.ts"],
    // 仅本应用测试
    include: ["tests/**/*.test.ts"],
    // 排除 e2e 与依赖
    exclude: ["**/e2e/**", "**/node_modules/**"],
  },
});
