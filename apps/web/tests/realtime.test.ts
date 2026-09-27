/** 实时传输测试 */
import { describe, expect, it, vi } from "vitest";
import { createWsTransport } from "../src/adapters/realtime";

describe("realtime transport", () => {
  it("createWsTransport 返回 Transport 接口", () => {
    const transport = createWsTransport("ws://localhost/ws");

    expect(transport.connect).toBeTypeOf("function");
    expect(transport.send).toBeTypeOf("function");
    expect(transport.close).toBeTypeOf("function");
  });

  it("send 调用 WebSocket.send", () => {
    // 桩 WebSocket
    const sendMock = vi.fn();
    const closeMock = vi.fn();
    class MockWebSocket {
      send = sendMock;
      close = closeMock;
      // 事件监听桩
      addEventListener = vi.fn();
    }
    vi.stubGlobal("WebSocket", MockWebSocket);

    const transport = createWsTransport("ws://localhost/ws");
    transport.connect(
      () => undefined,
      () => undefined,
      () => undefined,
    );
    transport.send("ping");

    expect(sendMock).toHaveBeenCalledWith("ping");
  });
});
