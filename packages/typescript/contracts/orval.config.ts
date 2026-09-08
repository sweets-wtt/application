/** Orval - https://orval.dev/reference/configuration/overview */
import { defineConfig } from "orval";

export default defineConfig({
  // 契约客户端
  contracts: {
    // 输入
    input: {
      target: "../../../contracts/http/openapi.yaml",
    },

    // 输出
    output: {
      client: "vue-query",
      mode: "tags-split",
      target: "./src/http",

      // 模式定义
      schemas: {
        path: "./src/schemas",
        type: "zod",
      },

      // 模拟
      mock: {
        generators: [{ type: "msw" }],
      },

      // 覆盖
      override: {
        // 自定义客户端
        mutator: {
          path: "./client.ts",
          name: "appFetch",
        },
      },
    },
  },
});
