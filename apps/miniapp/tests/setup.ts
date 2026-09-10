/** 测试初始化 */
import { vi } from "vitest";

// uni 运行时桩
vi.stubGlobal("uni", {
  getStorageSync: vi.fn(() => ""),
  setStorageSync: vi.fn(),
  removeStorageSync: vi.fn(),
  request: vi.fn(),
});

// 阻断网络
vi.stubGlobal(
  "fetch",
  vi.fn(() => {
    throw new Error("单元测试禁止网络");
  }),
);
