import { useDocumentVisibility } from "@vueuse/core";
import { computed } from "vue";

import { Healthz200Response, useGetHealthz } from "@/api";
import { HEARTBEAT_INTERVAL, SERVER_STATUS } from "@/features/health/constants";
import { logger } from "@/lib/logger";

import type { ServerStatus } from "@/features/health/constants";
import type { ComputedRef, Ref } from "vue";

/** 重试次数：失败重试一次 */
const RETRY_COUNT = 1;

/**
 * 按契约校验响应：不符时上报并丢弃
 *
 * @param {unknown} payload 待校验的响应数据
 * @returns {Healthz200Response | undefined} 合法时返回数据，否则为 undefined
 */
const validate = (payload: unknown): Healthz200Response | undefined => {
  // 数据未就绪时不校验
  if (payload === undefined) {
    return undefined;
  }

  const result = Healthz200Response.safeParse(payload);

  // 契约不符仅上报，不中断渲染
  if (!result.success) {
    logger.warn("响应不符合契约", { issues: result.error.issues.length });
    return undefined;
  }

  return result.data;
};

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

/**
 * 健康检查 hook：轮询存活探针并推导在线状态
 *
 * @returns {HealthCheckResult} 在线状态、请求状态与响应数据
 */
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
      retry: RETRY_COUNT,
    },
  });
  // 由请求结果推导在线状态
  const status = computed<ServerStatus>(() => {
    // 请求成功即在线
    if (isSuccess.value) {
      return SERVER_STATUS.online;
    }
    // 请求失败即离线
    if (isError.value) {
      return SERVER_STATUS.offline;
    }
    // 首次请求未完成
    return SERVER_STATUS.checking;
  });
  // 是否在线
  const online = computed(() => status.value === SERVER_STATUS.online);
  // 按契约校验响应信封
  const data = computed<Healthz200Response | undefined>(() => validate(result.value?.data));

  return { data, isFetching, online, status };
};
