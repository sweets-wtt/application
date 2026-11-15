import { z } from "zod";

/** 存储键 */
export const STORAGE_KEY = "app";

/** 当前状态版本 */
const CURRENT_VERSION = "1";

/** 缺省版本：无版本字段时视为最早版本 */
const DEFAULT_VERSION = "0";

/** 迁移最大迭代次数，防止迁移表成环 */
const MAX_MIGRATION_STEPS = 16;

/** 迁移循环起始步数 */
const INITIAL_STEP = 0;

/** 每次迁移的步长 */
const STEP_INCREMENT = 1;

/** 状态模式（版本化） */
const stateSchema = z.object({ locale: z.enum(["zh-CN", "en-US"]), version: z.literal(CURRENT_VERSION) });

/** 应用状态 */
export type State = z.infer<typeof stateSchema>;

/** 默认状态 */
export const defaultState: State = { locale: "zh-CN", version: CURRENT_VERSION };

/** 相邻迁移表：键为源版本，值返回升一级后的数据 */
const migrations: Record<string, (state: Readonly<Record<string, unknown>>) => Record<string, unknown>> = {};

/**
 * 读取版本号：字段非字符串时回退到给定值
 *
 * @param {Record<string, unknown>} state 待读取的状态对象
 * @param {string} fallback 无法读取时的回退值
 * @returns {string} 版本号
 */
const readVersion = (state: Readonly<Record<string, unknown>>, fallback: string): string => {
  // 合法版本号必须为字符串
  if (typeof state["version"] === "string") {
    return state["version"];
  }

  return fallback;
};

/**
 * 版本匹配则返回数据，否则返回 undefined
 *
 * @param {Record<string, unknown>} current 当前数据
 * @param {string} version 数据版本
 * @returns {Record<string, unknown> | undefined} 匹配时返回数据，否则为 undefined
 */
const settle = (current: Readonly<Record<string, unknown>>, version: string): Record<string, unknown> | undefined => {
  // 仅当前版本可直接使用
  if (version === CURRENT_VERSION) {
    return current;
  }

  return undefined;
};

/**
 * 逐级迁移到当前版本：无对应迁移或超出迭代上限则返回 undefined
 *
 * @param {Record<string, unknown>} data 待迁移的原始数据
 * @returns {Record<string, unknown> | undefined} 迁移结果，失败时为 undefined
 */
export const migrate = (data: Readonly<Record<string, unknown>>): Record<string, unknown> | undefined => {
  let current = data;
  let version = readVersion(current, DEFAULT_VERSION);

  // 逐级升级，迭代次数上限防止迁移表成环
  for (let step = INITIAL_STEP; version !== CURRENT_VERSION && step < MAX_MIGRATION_STEPS; step += STEP_INCREMENT) {
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

/** 原始状态模式：仅校验是普通对象，结构交由迁移与版本校验处理 */
const rawSchema = z.record(z.string(), z.unknown());

/**
 * 解析原始文本：格式损坏返回 undefined
 *
 * @param {string} raw 原始 JSON 文本
 * @returns {Record<string, unknown> | undefined} 解析结果，失败时为 undefined
 */
const parseRaw = (raw: string): Record<string, unknown> | undefined => {
  try {
    // 先按未知类型接收，再校验为普通对象
    const parsed = rawSchema.safeParse(JSON.parse(raw));

    // 非普通对象视为损坏
    if (!parsed.success) {
      return undefined;
    }

    return parsed.data;
  } catch {
    return undefined;
  }
};

/**
 * 校验迁移结果：失败回退默认状态
 *
 * @param {Record<string, unknown> | undefined} migrated 迁移后的数据
 * @returns {State} 合法的应用状态
 */
const validateMigrated = (migrated: Readonly<Record<string, unknown>> | undefined): State => {
  // 迁移失败直接回退
  if (migrated === undefined) {
    return defaultState;
  }

  const result = stateSchema.safeParse(migrated);

  // 结构不符时回退默认状态
  if (result.success) {
    return result.data;
  }

  return defaultState;
};

/**
 * 解析并迁移到当前版本：损坏或无法迁移的数据回退默认状态
 *
 * @param {string | null} [raw] 原始存储文本，缺失视为无内容
 * @returns {State} 应用状态
 */
export const parseState = (raw?: string | null): State => {
  // 非字符串即无存储内容，null、undefined 均视为缺失
  if (typeof raw !== "string") {
    return defaultState;
  }

  const parsed = parseRaw(raw);

  // JSON 损坏
  if (parsed === undefined) {
    return defaultState;
  }

  return validateMigrated(migrate(parsed));
};

/**
 * 序列化为 JSON 字符串
 *
 * @param {Readonly<Record<PropertyKey, unknown>>} state 只读状态树
 * @returns {string} JSON 文本
 */
export const serializeState = (state: Readonly<Record<PropertyKey, unknown>>): string => JSON.stringify(state);

/** 存储边界：仅依赖读写两项能力 */
export interface Storage {
  readonly getItem: (key: string) => string | null | undefined;
  readonly setItem: (key: string, value: string) => void;
}

/**
 * 从存储读取状态
 *
 * @param {Storage} storage 存储实现
 * @returns {State} 应用状态
 */
export const loadState = (storage: Storage): State => parseState(storage.getItem(STORAGE_KEY));

/**
 * 将状态写入存储
 *
 * @param {Storage} storage 存储实现
 * @param {State} state 应用状态
 */
export const saveState = (storage: Storage, state: Readonly<State>): void => {
  storage.setItem(STORAGE_KEY, serializeState(state));
};
