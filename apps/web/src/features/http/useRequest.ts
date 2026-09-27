/** HTTP 请求封装 */
import { useQuery } from "@tanstack/vue-query";
import type { UseQueryOptions } from "@tanstack/vue-query";

/** 通用请求封装：契约客户端 + useQuery */
export const useRequest = <T>(
  key: readonly unknown[],
  fn: () => Promise<T>,
  options?: Partial<UseQueryOptions<T>>,
) =>
  useQuery<T>({
    queryKey: key,
    queryFn: fn,
    ...options,
  });
