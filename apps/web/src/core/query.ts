/** TanStack Query 客户端 */
import { QueryClient } from "@tanstack/vue-query";

// 全局查询客户端
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // 窗口失焦不重新请求
      refetchOnWindowFocus: false,
    },
  },
});
