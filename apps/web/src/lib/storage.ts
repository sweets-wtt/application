import { z } from "zod";

// 存储键
export const STORAGE_KEY = "app";

// 当前状态版本
const CURRENT_VERSION = "1",
  // 状态模式（版本化）
  stateSchema = z.object({
    locale: z.enum(["zh-CN", "en-US"]),
    version: z.literal(CURRENT_VERSION),
  });

// 状态
export type State = z.infer<typeof stateSchema>;

// 默认状态
export const defaultState: State = { locale: "zh-CN", version: CURRENT_VERSION };

// 相邻迁移（旧版本 → 下一版本）
// 键为源版本，值返回升一级后的数据；缺失版本视为最早版本
const migrations: Record<string, (state: Record<string, unknown>) => Record<string, unknown>> = {};

/** 逐级迁移到当前版本：无对应迁移或过程中出错则返回 null */
export const migrate = (data: Record<string, unknown>): Record<string, unknown> | null => {
  let current = data,
    version = typeof current.version === "string" ? current.version : "0";

  // 逐级升级，最多迭代次数防止迁移表成环
  for (let step = 0; version !== CURRENT_VERSION && step < 16; step += 1) {
    const upgrade = migrations[version];

    if (upgrade === undefined) {
      return version === CURRENT_VERSION ? current : null;
    }

    current = upgrade(current);
    version = typeof current.version === "string" ? current.version : version;
  }

  return version === CURRENT_VERSION ? current : null;
};

/** 解析并迁移到当前版本：损坏或无法迁移的数据回退默认状态 */
export const parseState = (raw: string | null): State => {
  if (raw === null) {
    return defaultState;
  }

  let data: Record<string, unknown>;

  try {
    data = JSON.parse(raw) as Record<string, unknown>;
  } catch {
    return defaultState;
  }

  const migrated = migrate(data),
    result = migrated === null ? null : stateSchema.safeParse(migrated);

  return result?.success === true ? result.data : defaultState;
};

/** 序列化 */
export const serializeState = (state: State): string => JSON.stringify(state);

/** Storage 边界 */
export interface Storage {
  getItem: (key: string) => string | null;
  setItem: (key: string, value: string) => void;
}

/** 读取 */
export const loadState = (storage: Storage): State => parseState(storage.getItem(STORAGE_KEY));

/** 保存 */
export const saveState = (storage: Storage, state: State): void => {
  storage.setItem(STORAGE_KEY, serializeState(state));
};
