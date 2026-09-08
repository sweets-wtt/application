/** 阻断网络 */
import { beforeAll, vi } from "vitest";

beforeAll(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(() => {
      throw new Error("单元测试禁止网络");
    }),
  );
});
