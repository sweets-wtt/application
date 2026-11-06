import { describe, expect, it } from "vitest";

import {
  STORAGE_KEY,
  defaultState,
  loadState,
  migrate,
  parseState,
  saveState,
  serializeState,
} from "@/lib/storage";

import type { State, Storage } from "@/lib/storage";

/** 内存存储：替代 localStorage */
const memory = (initial: Record<string, string> = {}): Storage => {
  const data = { ...initial };

  return {
    getItem: (key: string): string | null => data[key] ?? null,
    setItem: (key: string, value: string): void => {
      data[key] = value;
    },
  };
};

describe("parseState", () => {
  it("空数据回退默认状态", () => {
    // 无存储内容直接回退
    expect(parseState(null)).toStrictEqual(defaultState);
  }, 5000);

  it("合法数据解析为状态", () => {
    // 当前版本数据原样解析
    expect(parseState('{"version":"1","locale":"en-US"}')).toStrictEqual({
      locale: "en-US",
      version: "1",
    });
  }, 5000);

  it("损坏 JSON 回退默认状态", () => {
    // 非 JSON 文本回退
    expect(parseState("{broken")).toStrictEqual(defaultState);
  }, 5000);

  it("未知版本回退默认状态", () => {
    // 无法迁移的版本回退
    expect(parseState('{"version":"9"}')).toStrictEqual(defaultState);
  }, 5000);
});

describe("migrate", () => {
  it("当前版本原样返回", () => {
    // 当前版本无需迁移
    const data = { locale: "en-US", version: "1" };

    expect(migrate(data)).toStrictEqual(data);
  }, 5000);

  it("缺失版本视为最早版本 - 无迁移时返回 null", () => {
    // 无对应迁移表项
    expect(migrate({ locale: "en-US" })).toBeNull();
  }, 5000);

  it("未知版本返回 null", () => {
    // 未知版本无法迁移
    expect(migrate({ version: "9" })).toBeNull();
  }, 5000);
});

describe("loadState/saveState", () => {
  it("保存后可读取", () => {
    // 写入后读回应一致
    const storage = memory();
    const state: State = { locale: "en-US", version: "1" };

    saveState(storage, state);

    expect(storage.getItem(STORAGE_KEY)).toBe(serializeState(state));
    expect(loadState(storage)).toStrictEqual(state);
  }, 5000);
});
