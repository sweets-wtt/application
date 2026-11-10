import { defineConfig, presetIcons, presetWind3 } from "unocss";

// 图标集按需自动解析（@iconify-json/carbon）
export default defineConfig({ presets: [presetWind3(), presetIcons()] });
