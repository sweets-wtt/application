import { type Healthz200Response, useGetHealthz } from "@/api";
import { HEARTBEAT_INTERVAL } from "@/features/health/constants";

/** 服务端状态 */
export type ServerStatus = "online" | "offline" | "checking";

/** 健康检查返回值 */
export interface HealthCheckResult {
  /** 在线状态 */
  status: ComputedRef<ServerStatus>;
  /** 是否在线 */
  online: ComputedRef<boolean>;
  /** 是否正在请求 */
  isFetching: Ref<boolean>;
  /** 响应数据 */
  data: ComputedRef<Healthz200Response | undefined>;
}

/** 健康检查 hook：轮询存活探针并推导在线状态 */
export const useHealthCheck = (): HealthCheckResult => {
  // 页面可见性：隐藏时暂停轮询，恢复时自动重取
  const visibility = useDocumentVisibility();
  // 仅页面可见时启用查询
  const enabled = computed(() => visibility.value === "visible");
  // 契约请求：定时拉取存活探针
  const {
    isSuccess,
    isError,
    isFetching,
    data: result,
  } = useGetHealthz({
    query: {
      // 页面可见时轮询
      enabled,
      // 轮询间隔
      refetchInterval: HEARTBEAT_INTERVAL,
      // 失败重试一次
      retry: 1,
    },
  });
  // 由请求结果推导在线状态
  const status = computed<ServerStatus>(() => {
    // 请求成功即在线
    if (isSuccess.value) {
      return "online";
    }
    // 请求失败即离线
    if (isError.value) {
      return "offline";
    }
    // 首次请求未完成
    return "checking";
  });
  // 是否在线
  const online = computed(() => status.value === "online");
  // 取响应信封内层数据
  const data = computed<Healthz200Response | undefined>(() => result.value?.data);

  return { data, isFetching, online, status };
};
