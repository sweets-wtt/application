/** 状态测试 */
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it } from "vitest";
import { useAppStore } from "@/stores/app";

describe("stores", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("应用状态可访问", () => {
    const store = useAppStore();
    expect(store.$id).toBe("app");
  });
});
