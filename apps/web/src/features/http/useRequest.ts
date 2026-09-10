/** HTTP 请求封装 */

import type { Healthz200 } from "@app/contracts";
import { healthz } from "@app/contracts";
import { useQuery } from "@tanstack/vue-query";

/** 存活探针查询 */
export function useHealthz() {
  return useQuery({
    queryKey: ["healthz"],
    queryFn: async () => {
      const response = await healthz();
      return response.data as Healthz200;
    },
  });
}
