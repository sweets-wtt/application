/** Vite - https://vite.dev/config/ */
import uniRaw from "@dcloudio/vite-plugin-uni";
import UnoCSS from "unocss/vite";
import { defineConfig } from "vite";

// CJS 默认导出兼容
const uni = ((uniRaw as unknown as { default?: typeof uniRaw }).default ?? uniRaw) as typeof uniRaw;

export default defineConfig({
  // 插件
  plugins: [uni(), UnoCSS()],

  // 解析
  resolve: {
    preserveSymlinks: false,
  },
});
