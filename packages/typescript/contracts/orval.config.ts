/** Orval - https://orval.dev/reference/configuration/overview */
import { defineConfig } from "orval";

export default defineConfig({
  // 契约客户端
  contracts: {
    // 输入
    input: {
      // 契约来源
      target: "../../../contracts/http/openapi.yaml",
    },

    // 输出
    output: {
      // 客户端
      client: "vue-query",
      // 输出模式
      mode: "tags-split",
      // 输出目录
      target: "./src/http",

      // 模式定义
      schemas: {
        // 模式目录
        path: "./src/schemas",
        // 校验器类型
        type: "zod",
      },

      // 模拟
      mock: {
        // 生成器
        generators: [{ type: "msw" }],
      },

      // 覆盖
      override: {
        // 自定义客户端
        mutator: {
          // 文件路径
          path: "./client.ts",
          // 函数名
          name: "appFetch",
        },
      },
    },
  },
});
