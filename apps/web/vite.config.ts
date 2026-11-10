import vue from "@vitejs/plugin-vue";
import RekaResolver from "reka-ui/resolver";
import UnoCSS from "unocss/vite";
import AutoImport from "unplugin-auto-import/vite";
import IconsResolver from "unplugin-icons/resolver";
import Icons from "unplugin-icons/vite";
import Components from "unplugin-vue-components/vite";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [
    vue(),
    UnoCSS(),
    AutoImport({
      // 生成类型声明供 tsc 识别自动导入
      dts: "./auto-imports.d.ts",
      imports: [
        "vue",
        "pinia",
        "@vueuse/core",
        // 路由 preset 仅覆盖组合式 API，此处补全路由创建与工具函数
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
        // 自动导入类型，不注入运行时导入
        { from: "vue-router", imports: ["RouteRecordRaw"], type: true },
      ],
      include: [/\.[jt]sx?$/, /\.vue$/, /\.vue\?vue/, /\.vue\.[jt]sx?\?vue/],
    }),
    Components({
      // 生成物会与格式化规则冲突，故关闭
      dts: false,
      resolvers: [IconsResolver({ prefix: "icon" }), RekaResolver()],
    }),
    Icons({ autoInstall: false }),
  ],

  resolve: { alias: { "@": `${import.meta.dirname}/src` } },

  test: {
    environment: "jsdom",
    exclude: ["**/e2e/**", "**/node_modules/**"],
    include: ["tests/**/*.test.ts"],
    // 使用 threads 池：forks 池在 Windows 下临时目录会 EPERM
    pool: "threads",
    setupFiles: ["./tests/setup.ts"],
    // 单测试超时（毫秒）
    testTimeout: 5000,
  },
});
