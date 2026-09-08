/** 持久化状态 */
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

/** 解析并迁移到当前版本 */
export const parse = (raw: string | null): State => {
  if (raw === null) {
    return defaultState;
  }

  const data = JSON.parse(raw) as Record<string, unknown>;
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
