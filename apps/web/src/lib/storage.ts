import { z } from "zod";

/** 存储键 */
export const STORAGE_KEY = "app";

/** 当前状态版本 */
const CURRENT_VERSION = "1";

/** 缺省版本：无版本字段时视为最早版本 */
const DEFAULT_VERSION = "0";

/** 迁移最大迭代次数，防止迁移表成环 */
const MAX_MIGRATION_STEPS = 16;

/** 状态模式（版本化） */
const stateSchema = z.object({
  locale: z.enum(["zh-CN", "en-US"]),
  version: z.literal(CURRENT_VERSION),
});

/** 应用状态 */
export type State = z.infer<typeof stateSchema>;

/** 默认状态 */
export const defaultState: State = { locale: "zh-CN", version: CURRENT_VERSION };

/** 相邻迁移表：键为源版本，值返回升一级后的数据 */
const migrations: Record<string, (state: Record<string, unknown>) => Record<string, unknown>> = {};

/** 读取版本号：字段非字符串时回退到给定值 */
const readVersion = (state: Record<string, unknown>, fallback: string): string => {
  // 合法版本号必须为字符串
  if (typeof state["version"] === "string") {
    return state["version"];
  }

  return fallback;
};

/** 版本匹配则返回数据，否则返回 null */
const settle = (
  current: Record<string, unknown>,
  version: string,
): Record<string, unknown> | null => {
  // 仅当前版本可直接使用
  if (version === CURRENT_VERSION) {
    return current;
  }

  return null;
};

/** 逐级迁移到当前版本：无对应迁移或超出迭代上限则返回 null */
export const migrate = (data: Record<string, unknown>): Record<string, unknown> | null => {
  let current = data;
  let version = readVersion(current, DEFAULT_VERSION);

  // 逐级升级，迭代次数上限防止迁移表成环
  for (let step = 0; version !== CURRENT_VERSION && step < MAX_MIGRATION_STEPS; step += 1) {
    const upgrade = migrations[version];

    // 缺少对应迁移，无法继续
    if (upgrade === undefined) {
      return settle(current, version);
    }

    current = upgrade(current);
    version = readVersion(current, version);
  }

  return settle(current, version);
};

/** 解析原始文本：格式损坏返回 null */
const parseRaw = (raw: string): Record<string, unknown> | null => {
  try {
    return JSON.parse(raw) as Record<string, unknown>;
  } catch {
    return null;
  }
};

/** 校验迁移结果：失败回退默认状态 */
const validateMigrated = (migrated: Record<string, unknown> | null): State => {
  // 迁移失败直接回退
  if (migrated === null) {
    return defaultState;
  }

  const result = stateSchema.safeParse(migrated);

  // 结构不符时回退默认状态
  if (result.success) {
    return result.data;
  }

  return defaultState;
};

/** 解析并迁移到当前版本：损坏或无法迁移的数据回退默认状态 */
export const parseState = (raw: string | null): State => {
  // 无存储内容
  if (raw === null) {
    return defaultState;
  }

  const parsed = parseRaw(raw);

  // JSON 损坏
  if (parsed === null) {
    return defaultState;
  }

  return validateMigrated(migrate(parsed));
};

/** 序列化为 JSON 字符串 */
export const serializeState = (state: State): string => JSON.stringify(state);

/** 存储边界：仅依赖读写两项能力 */
export interface Storage {
  getItem: (key: string) => string | null;
  setItem: (key: string, value: string) => void;
}

/** 从存储读取状态 */
export const loadState = (storage: Storage): State => parseState(storage.getItem(STORAGE_KEY));

/** 将状态写入存储 */
export const saveState = (storage: Storage, state: State): void => {
  storage.setItem(STORAGE_KEY, serializeState(state));
};
