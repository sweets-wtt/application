/** 持久化状态与会话令牌 */
import { z } from "zod";

// 存储键
export const STORAGE_KEY = "app";

// 状态模式（版本化）
const stateSchema = z.object({
  version: z.literal("1"),
  locale: z.enum(["zh-CN", "en-US"]),
});

// 状态
export type State = z.infer<typeof stateSchema>;

// 默认状态
export const defaultState: State = { version: "1", locale: "zh-CN" };

// 相邻迁移（旧版本 → 下一版本）
const migrations: Record<string, (state: Record<string, unknown>) => Record<string, unknown>> = {};

/** 解析并迁移到当前版本：损坏数据回退默认状态 */
export const parse = (raw: string | null): State => {
  if (raw === null) {
    return defaultState;
  }

  let data: Record<string, unknown>;

  try {
    data = JSON.parse(raw) as Record<string, unknown>;
  } catch {
    return defaultState;
  }

  const version = typeof data.version === "string" ? data.version : "1";
  const migrated = migrations[version]?.(data) ?? data;

  return stateSchema.safeParse(migrated).success ? stateSchema.parse(migrated) : defaultState;
};

/** 序列化 */
export const serialize = (state: State): string => JSON.stringify(state);

/** storage 边界 */
export interface Storage {
  getItem: (key: string) => string | null;
  setItem: (key: string, value: string) => void;
}

/** 读取 */
export const load = (storage: Storage): State => parse(storage.getItem(STORAGE_KEY));

/** 保存 */
export const save = (storage: Storage, state: State): void => {
  storage.setItem(STORAGE_KEY, serialize(state));
};

// 会话模式
const sessionSchema = z.object({
  // 访问令牌
  token: z.string(),
  // 刷新令牌
  refresh: z.string(),
  // 过期时间（epoch 毫秒）
  expiresAt: z.number(),
});

// 会话
export type Session = z.infer<typeof sessionSchema>;

// 会话存储键
const SESSION_KEY = "app.session";

// 默认续期提前量（毫秒）
const RENEW_MARGIN_MS = 60_000;

/** 令牌过期判断 */
export const isExpired = (expiresAt: number, now: number = Date.now()): boolean => expiresAt <= now;

/** 认证守卫谓词：会话合法且未过期 */
export const authGuard = (session: unknown, now: number = Date.now()): session is Session => {
  const result = sessionSchema.safeParse(session);

  return result.success && !isExpired(result.data.expiresAt, now);
};

/** Bearer 注入 */
export const bearer = (token: string): Record<string, string> => ({
  Authorization: `Bearer ${token}`,
});

/** 静默续期调度：到期前 margin 触发续期，返回取消函数 */
export const scheduleRenewal = (
  expiresAt: number,
  renew: () => void | Promise<void>,
  marginMs: number = RENEW_MARGIN_MS,
): (() => void) => {
  const delay = Math.max(0, expiresAt - marginMs - Date.now());
  const timer = setTimeout(() => {
    void renew();
  }, delay);

  return () => clearTimeout(timer);
};

/** 读取会话：缺失、空串或非法返回 undefined */
export const loadSession = (storage: Storage): Session | undefined => {
  const raw = storage.getItem(SESSION_KEY);

  if (raw === null || raw === "") {
    return undefined;
  }

  try {
    const result = sessionSchema.safeParse(JSON.parse(raw) as unknown);

    return result.success ? result.data : undefined;
  } catch {
    return undefined;
  }
};

/** 保存会话 */
export const saveSession = (storage: Storage, session: Session): void => {
  storage.setItem(SESSION_KEY, JSON.stringify(session));
};

/** 清除会话 */
export const clearSession = (storage: Storage): void => {
  storage.setItem(SESSION_KEY, "");
};
