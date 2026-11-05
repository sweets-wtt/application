import { describe, expect, it } from "vitest";

import {
  STORAGE_KEY,
  type State,
  defaultState,
  loadState,
  migrate,
  parseState,
  saveState,
  serializeState,
} from "@/lib/storage";

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

describe("parseState", () => {
  it("空数据回退默认状态", () => {
    expect(parseState(null)).toStrictEqual(defaultState);
  });

  it("合法数据解析为状态", () => {
    expect(parseState('{"version":"1","locale":"en-US"}')).toStrictEqual({
      locale: "en-US",
      version: "1",
    });
  });

  it("损坏 JSON 回退默认状态", () => {
    expect(parseState("{broken")).toStrictEqual(defaultState);
  });

  it("未知版本回退默认状态", () => {
    expect(parseState('{"version":"9"}')).toStrictEqual(defaultState);
  });
});

describe("migrate", () => {
  it("当前版本原样返回", () => {
    const data = { locale: "en-US", version: "1" };

    expect(migrate(data)).toStrictEqual(data);
  });

  it("缺失版本视为最早版本 - 无迁移时返回 null", () => {
    expect(migrate({ locale: "en-US" })).toBeNull();
  });

  it("未知版本返回 null", () => {
    expect(migrate({ version: "9" })).toBeNull();
  });
});

describe("loadState/saveState", () => {
  it("保存后可读取", () => {
    const storage = memory(),
      state: State = { locale: "en-US", version: "1" };

    saveState(storage, state);

    expect(storage.getItem(STORAGE_KEY)).toBe(serializeState(state));
    expect(loadState(storage)).toStrictEqual(state);
  });
});
