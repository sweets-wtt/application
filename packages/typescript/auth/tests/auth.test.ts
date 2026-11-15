/** 会话与令牌测试 */
import { describe, expect, it, vi } from "vitest";
import {
  authGuard,
  bearer,
  clearSession,
  isExpired,
  loadSession,
  saveSession,
  scheduleRenewal,
} from "../src/index";

// 有效会话
const session = { token: "t", refresh: "r", expiresAt: Date.now() + 60_000 };

/** 内存存储 */
const memory = (initial: Record<string, string> = {}) => {
  const data = { ...initial };

  return {
    getItem: (key: string) => data[key] ?? null,
    setItem: (key: string, value: string) => {
      data[key] = value;
    },
  };
};

describe("isExpired", () => {
  it("过期时间为过去则已过期", () => {
    expect(isExpired(Date.now() - 1_000, Date.now())).toBe(true);
  });

  it("过期时间为未来则未过期", () => {
    expect(isExpired(Date.now() + 60_000, Date.now())).toBe(false);
  });
});

describe("authGuard", () => {
  it("合法且未过期通过", () => {
    expect(authGuard(session, Date.now())).toBe(true);
  });

  it("已过期不通过", () => {
    expect(authGuard({ ...session, expiresAt: Date.now() - 1_000 }, Date.now())).toBe(false);
  });

  it("非法结构不通过", () => {
    expect(authGuard({ token: 1 }, Date.now())).toBe(false);
  });
});

describe("bearer", () => {
  it("注入 Bearer 头", () => {
    expect(bearer("t")).toEqual({ Authorization: "Bearer t" });
  });
});

describe("scheduleRenewal", () => {
  it("到期前 margin 触发续期", () => {
    vi.useFakeTimers();
    try {
      let renewed = false;
      scheduleRenewal(Date.now() + 120_000, () => {
        renewed = true;
      });

      vi.advanceTimersByTime(59_999);
      expect(renewed).toBe(false);

      vi.advanceTimersByTime(1);
      expect(renewed).toBe(true);
    } finally {
      vi.useRealTimers();
    }
  });

  it("返回取消函数可阻止续期", () => {
    vi.useFakeTimers();
    try {
      let renewed = false;
      const cancel = scheduleRenewal(Date.now() + 120_000, () => {
        renewed = true;
      });

      cancel();
      vi.advanceTimersByTime(120_000);

      expect(renewed).toBe(false);
    } finally {
      vi.useRealTimers();
    }
  });
});

describe("会话持久化", () => {
  it("保存后可读取", () => {
    const storage = memory();

    saveSession(storage, session);

    expect(loadSession(storage)).toEqual(session);
  });

  it("缺失返回 undefined", () => {
    expect(loadSession(memory())).toBeUndefined();
  });

  it("非法数据返回 undefined", () => {
    const storage = memory();
    storage.setItem("app.session", '{"token":1}');

    expect(loadSession(storage)).toBeUndefined();
  });

  it("清除后返回 undefined", () => {
    const storage = memory();

    saveSession(storage, session);
    clearSession(storage);

    expect(loadSession(storage)).toBeUndefined();
  });
});
