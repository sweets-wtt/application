import vue from "@vitejs/plugin-vue";
import RekaResolver from "reka-ui/resolver";
import UnoCSS from "unocss/vite";
import IconsResolver from "unplugin-icons/resolver";
import Icons from "unplugin-icons/vite";
import Components from "unplugin-vue-components/vite";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [
    vue(),
    UnoCSS(),
    Components({
      // 类型声明路径
      dts: "./components.d.ts",
      resolvers: [IconsResolver({ prefix: "icon" }), RekaResolver()],
    }),
    Icons({ autoInstall: false }),
  ],

  resolve: { alias: { "@": `${import.meta.dirname}/src` } },

  test: {
    environment: "jsdom",
    exclude: ["**/e2e/**", "**/node_modules/**"],
    include: ["tests/**/*.test.ts"],
    // 工作池
    pool: "threads",
    setupFiles: ["./tests/setup.ts"],
    // 测试超时
    testTimeout: 5000,
  },
});
