import { beforeEach, describe, expect, it, vi } from "vitest";

/** 模拟的查询状态 */
const query = vi.hoisted(() => ({
  data: { value: undefined as unknown },
  isError: { value: false },
  isFetching: { value: false },
  isSuccess: { value: true },
}));

/** 模拟的日志告警 */
const warn = vi.hoisted(() => vi.fn<(message: string, data?: Record<string, unknown>) => void>());

vi.mock(import("@/api"), async (importOriginal) => {
  const actual = await importOriginal();

  return { ...actual, useGetHealthz: (() => query) as typeof actual.useGetHealthz };
});

vi.mock(import("@/lib/logger"), () => ({
  logger: {
    error: vi.fn<(message: string, data?: Record<string, unknown>) => void>(),
    info: vi.fn<(message: string, data?: Record<string, unknown>) => void>(),
    warn,
  },
}));

import { useHealthCheck } from "@/features/health/composables/useHealthCheck";

/** 合法响应信封 */
const VALID = { code: 0, data: { status: "ok" }, message: "ok" };

/** 非法响应信封：status 不在枚举内 */
const INVALID = { code: 0, data: { status: "invalid" }, message: "ok" };

/**
 * 构造查询返回值：data 字段为响应信封
 *
 * @param {unknown} body 响应信封
 * @returns {Record<string, unknown>} 查询返回值
 */
const response = (body: unknown): Record<string, unknown> => ({ data: body, headers: new Headers(), status: 200 });

describe("useHealthCheck", () => {
  beforeEach(() => {
    // 每个用例重置模拟状态
    query.data.value = undefined;
    query.isError.value = false;
    query.isSuccess.value = true;
    warn.mockClear();
  });

  it("合法响应通过校验", () => {
    // 契约相符时返回数据
    query.data.value = response(VALID);

    const { data } = useHealthCheck();

    expect(data.value).toStrictEqual(VALID);
    expect(warn).not.toHaveBeenCalled();
  });

  it("非法响应丢弃并上报", () => {
    // 契约不符时不上报给视图
    query.data.value = response(INVALID);

    const { data } = useHealthCheck();

    expect(data.value).toBeUndefined();
    // 告警消息固定，issues 仅要求为数字而不绑定具体条数
    expect(warn).toHaveBeenCalledWith("响应不符合契约", expect.objectContaining({ issues: expect.any(Number) }));
  });

  it("数据未就绪时不校验", () => {
    // 首次加载未产生告警
    const { data } = useHealthCheck();

    expect(data.value).toBeUndefined();
    expect(warn).not.toHaveBeenCalled();
  });
});
