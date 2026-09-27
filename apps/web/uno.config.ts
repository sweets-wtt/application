/** UnoCSS 配置 */
import { defineConfig, presetWind3, presetIcons } from "unocss";

export default defineConfig({
  // 预设
  presets: [
    // 原子样式（Windi CSS v3）
    presetWind3(),
    // 图标
    presetIcons({
      // 启用图标集
      enabledCollections: ["carbon"],
    }),
  ],
});
