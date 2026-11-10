import { describe, expect, it } from "vitest";

import { DEFAULT_HEARTBEAT_INTERVAL, parseHeartbeatInterval } from "@/features/health/constants";

/** 测试用心跳间隔 */
const TEST_INTERVAL = "5000";

describe("parseHeartbeatInterval", () => {
  it("解析正整数", () => {
    // 合法数字原样返回
    expect(parseHeartbeatInterval(TEST_INTERVAL)).toBe(Number(TEST_INTERVAL));
  });

  it("未注入回退默认", () => {
    // 参数缺省时回退
    expect(parseHeartbeatInterval()).toBe(DEFAULT_HEARTBEAT_INTERVAL);
  });

  it("空串回退默认", () => {
    // 空串不得解析为 0
    expect(parseHeartbeatInterval("")).toBe(DEFAULT_HEARTBEAT_INTERVAL);
  });

  it("非数字回退默认", () => {
    // NaN 回退默认
    expect(parseHeartbeatInterval("abc")).toBe(DEFAULT_HEARTBEAT_INTERVAL);
  });

  it("非正值回退默认", () => {
    // 零与负数均回退
    expect(parseHeartbeatInterval("0")).toBe(DEFAULT_HEARTBEAT_INTERVAL);
    expect(parseHeartbeatInterval("-1")).toBe(DEFAULT_HEARTBEAT_INTERVAL);
  });
});
