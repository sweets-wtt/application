/** 实时组合式函数 */
import { onBeforeUnmount, onMounted, ref } from "vue";
import { RealtimeClient, type Status } from "@app/realtime";
import { createWsTransport } from "@/adapters/realtime";

/** 实时 composable：特性未启用则不注册 */
export const useRealtime = (
  url: string,
  acquireTicket: () => Promise<{ ticket: string; expiresAtMs: number }>,
) => {
  // 连接状态
  const status = ref<Status>("disconnected");

  // 客户端实例
  let client: RealtimeClient | undefined;

  // 挂载时连接
  onMounted(() => {
    // 未启用实时特性则跳过
    if (!url) {
      return;
    }

    client = new RealtimeClient({
      transport: () => createWsTransport(url),
      acquireTicket,
      // 票据应用：连接时通过查询参数传递
      applyTicket: (transport, ticket) => transport.send(JSON.stringify({ ticket })),
      onEvent: (event) => {
        // 契约事件回调
        console.debug("realtime event", event);
      },
    });

    client.connect();
    status.value = client.status;
  });

  // 卸载时关闭
  onBeforeUnmount(() => {
    client?.close();
    client = undefined;
  });

  return { status };
};
