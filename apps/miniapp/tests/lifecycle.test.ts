/** 生命周期测试 */
import { describe, expect, it } from "vitest";
import {
  onHide,
  onLaunch,
  onShow,
  tryOnHide,
  tryOnLoad,
  tryOnShow,
  tryOnUnload,
} from "@/core/lifecycle";

describe("lifecycle", () => {
  it("生命周期可组合", () => {
    expect(typeof onLaunch).toBe("function");
    expect(typeof onShow).toBe("function");
    expect(typeof onHide).toBe("function");
    expect(typeof tryOnLoad).toBe("function");
    expect(typeof tryOnShow).toBe("function");
    expect(typeof tryOnHide).toBe("function");
    expect(typeof tryOnUnload).toBe("function");
  });
});
