/** 服务端健康检查（心跳） */
import { computed, type ComputedRef, type Ref } from "vue";
import { useRequest } from "@/features/http/useRequest";
import { clientFetch } from "@/adapters/http";
import type { Healthz200 } from "@app/contracts";
import { HEARTBEAT_INTERVAL } from "@/core/settings";

/** 服务端状态 */
export type ServerStatus = "online" | "offline" | "checking";

/** 健康检查返回值 */
export interface HealthCheckResult {
  status: ComputedRef<ServerStatus>;
  online: ComputedRef<boolean>;
  isFetching: Ref<boolean>;
  data: Ref<Healthz200 | undefined>;
}

/** 健康检查 hook：轮询 /healthz 并推导在线状态 */
export const useHealthCheck = (): HealthCheckResult => {
  // 契约请求：定时拉取存活探针
  const { isSuccess, isError, isFetching, data } = useRequest<Healthz200>(
    ["healthz"],
    () => clientFetch<Healthz200>("/healthz"),
    {
      // 轮询间隔
      refetchInterval: HEARTBEAT_INTERVAL,
      // 失败重试一次
      retry: 1,
    },
  );

  // 在线状态
  const status = computed<ServerStatus>(() => {
    if (isSuccess.value) {
      return "online";
    }
    if (isError.value) {
      return "offline";
    }
    return "checking";
  });

  // 是否在线
  const online = computed(() => status.value === "online");

  return { status, online, isFetching, data };
};
