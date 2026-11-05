import { describe, expect, it } from "vitest";

import { DEFAULT_HEARTBEAT_INTERVAL, parseHeartbeatInterval } from "@/features/health/constants";

describe("parseHeartbeatInterval", () => {
  it("解析正整数", () => {
    expect(parseHeartbeatInterval("5000")).toBe(5000);
  });

  it("未注入回退默认", () => {
    expect(parseHeartbeatInterval()).toBe(DEFAULT_HEARTBEAT_INTERVAL);
  });

  it("空串回退默认", () => {
    expect(parseHeartbeatInterval("")).toBe(DEFAULT_HEARTBEAT_INTERVAL);
  });

  it("非数字回退默认", () => {
    expect(parseHeartbeatInterval("abc")).toBe(DEFAULT_HEARTBEAT_INTERVAL);
  });

  it("非正值回退默认", () => {
    expect(parseHeartbeatInterval("0")).toBe(DEFAULT_HEARTBEAT_INTERVAL);
    expect(parseHeartbeatInterval("-1")).toBe(DEFAULT_HEARTBEAT_INTERVAL);
  });
});
