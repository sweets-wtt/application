/** 实时传输：浏览器 WebSocket */
import type { Transport } from "@app/realtime";

/** 创建 WebSocket 传输 */
export const createWsTransport = (url: string): Transport => {
  let socket: WebSocket | undefined;

  return {
    // 建立连接并挂接回调
    connect(onMessage, onClose, onError) {
      socket = new WebSocket(url);
      socket.addEventListener("message", (event) => onMessage(event.data as string));
      socket.addEventListener("close", () => onClose());
      socket.addEventListener("error", (error) => onError(error));
    },
    // 发送文本
    send(data) {
      socket?.send(data);
    },
    // 关闭连接
    close() {
      socket?.close();
    },
  };
};
