import vue from "@vitejs/plugin-vue";
import RekaResolver from "reka-ui/resolver";
import UnoCSS from "unocss/vite";
import AutoImport from "unplugin-auto-import/vite";
import IconsResolver from "unplugin-icons/resolver";
import Icons from "unplugin-icons/vite";
import Components from "unplugin-vue-components/vite";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [
    vue(),
    UnoCSS(),
    AutoImport({
      // 类型声明路径
      dts: "./auto-imports.d.ts",
      imports: [
        "vue",
        "pinia",
        "@vueuse/core",
        // 路由导入项
        {
          "vue-router": [
            "createRouter",
            "createRouterMatcher",
            "createWebHistory",
            "createWebHashHistory",
            "createMemoryHistory",
            "useRouter",
            "useRoute",
            "useLink",
            "onBeforeRouteLeave",
            "onBeforeRouteUpdate",
            "RouterLink",
            "RouterView",
            "isNavigationFailure",
            "loadRouteLocation",
            "parseQuery",
            "stringifyQuery",
            "START_LOCATION",
          ],
        },
        // 仅类型导入
        { from: "vue-router", imports: ["RouteRecordRaw"], type: true },
      ],
      include: [/\.[jt]sx?$/, /\.vue$/, /\.vue\?vue/, /\.vue\.[jt]sx?\?vue/],
    }),
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
