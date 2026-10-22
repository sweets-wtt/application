import type { RequestHandler } from "msw";

// 契约产生 tags 后由 orval 生成 handler,再导出 ./http/<tag>/<tag>.msw 的 handlers
export const handlers: RequestHandler[] = [];
