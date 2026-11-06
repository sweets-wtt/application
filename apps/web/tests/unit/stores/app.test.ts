import { describe, expect, it } from "vitest";

import useAppStore from "@/stores/app";

/** 每个用例使用独立 Pinia 实例 */
const createStore = (): ReturnType<typeof useAppStore> => {
  setActivePinia(createPinia());

  return useAppStore();
};

describe("app store", () => {
  it("可创建实例", () => {
    // 创建仓库实例
    const store = createStore();

    expect(store).toBeDefined();
  }, 5000);
});
