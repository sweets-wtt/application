import { beforeAll, vi } from "vitest";

// 单元测试禁止真实网络
beforeAll(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(() => {
      throw new Error("单元测试禁止网络");
    }),
  );
});
