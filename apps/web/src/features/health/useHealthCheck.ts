/** 服务端健康检查（心跳） */
import { computed, type ComputedRef, type Ref } from "vue";
import { useGetHealthz, type Healthz200Response } from "@/contracts";
import { HEARTBEAT_INTERVAL } from "@/core/settings";

/** 服务端状态 */
export type ServerStatus = "online" | "offline" | "checking";

/** 健康检查返回值 */
export interface HealthCheckResult {
  status: ComputedRef<ServerStatus>;
  online: ComputedRef<boolean>;
  isFetching: Ref<boolean>;
  data: ComputedRef<Healthz200Response | undefined>;
}

/** 健康检查 hook：轮询 /getHealthz 并推导在线状态 */
export const useHealthCheck = (): HealthCheckResult => {
  // 契约请求：定时拉取存活探针
  const {
    isSuccess,
    isError,
    isFetching,
    data: result,
  } = useGetHealthz({
    query: {
      // 轮询间隔
      refetchInterval: HEARTBEAT_INTERVAL,
      // 失败重试一次
      retry: 1,
    },
  });

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

  // 响应信封内层数据
  const data = computed<Healthz200Response | undefined>(() => result.value?.data);

  return { status, online, isFetching, data };
};
