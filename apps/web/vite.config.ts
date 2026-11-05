import { URL, fileURLToPath } from "node:url";

import vue from "@vitejs/plugin-vue";
import RekaResolver from "reka-ui/resolver";
import UnoCSS from "unocss/vite";
import IconsResolver from "unplugin-icons/resolver";
import Icons from "unplugin-icons/vite";
import Components from "unplugin-vue-components/vite";
import { defineConfig } from "vite";

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

  resolve: { alias: { "@": fileURLToPath(new URL("src", import.meta.url)) } },

  test: {
    environment: "jsdom",
    exclude: ["**/e2e/**", "**/node_modules/**"],
    include: ["tests/**/*.test.ts"],
    // Threads：forks 池在 Windows 下临时目录会 EPERM
    pool: "threads",
    setupFiles: ["./tests/setup.ts"],
  },
});
