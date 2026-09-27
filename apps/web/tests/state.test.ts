/** 状态持久化测试 */
import { setActivePinia, createPinia } from "pinia";
import { beforeEach, describe, expect, it } from "vitest";
import { useAppStore } from "../src/stores/app";

describe("app store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("可创建实例", () => {
    const store = useAppStore();

    expect(store).toBeDefined();
  });
});

