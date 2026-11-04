import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import UnoCSS from "unocss/vite";
import Components from "unplugin-vue-components/vite";
import Icons from "unplugin-icons/vite";
import IconsResolver from "unplugin-icons/resolver";
import RekaResolver from "reka-ui/resolver";

export default defineConfig({
  plugins: [
    vue(),
    UnoCSS(),
    Components({
      // 关闭 dts 生成，避免生成物与格式化/忽略规则冲突
      dts: false,
      resolvers: [IconsResolver({ prefix: "icon" }), RekaResolver()],
    }),
    Icons({ autoInstall: false }),
  ],

  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },

  test: {
    // threads：forks 池在 Windows 下临时目录会 EPERM
    pool: "threads",
    environment: "jsdom",
    setupFiles: ["./tests/setup.ts"],
    include: ["tests/**/*.test.ts"],
    exclude: ["**/e2e/**", "**/node_modules/**"],
  },
});
