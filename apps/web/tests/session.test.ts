import { describe, expect, it } from "vitest";
import {
  defaultState,
  load,
  migrate,
  parse,
  STORAGE_KEY,
  type State,
  save,
  serialize,
} from "../src/core/session";

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

describe("parse", () => {
  it("空数据回退默认状态", () => {
    expect(parse(null)).toEqual(defaultState);
  });

  it("合法数据解析为状态", () => {
    expect(parse('{"version":"1","locale":"en-US"}')).toEqual({
      version: "1",
      locale: "en-US",
    });
  });

  it("损坏 JSON 回退默认状态", () => {
    expect(parse("{broken")).toEqual(defaultState);
  });

  it("未知版本回退默认状态", () => {
    expect(parse('{"version":"9"}')).toEqual(defaultState);
  });
});

describe("migrate", () => {
  it("当前版本原样返回", () => {
    const data = { version: "1", locale: "en-US" };

    expect(migrate(data)).toEqual(data);
  });

  it("缺失版本视为最早版本 - 无迁移时返回 null", () => {
    expect(migrate({ locale: "en-US" })).toBeNull();
  });

  it("未知版本返回 null", () => {
    expect(migrate({ version: "9" })).toBeNull();
  });
});

describe("load/save", () => {
  it("保存后可读取", () => {
    const storage = memory();
    const state: State = { version: "1", locale: "en-US" };

    save(storage, state);

    expect(storage.getItem(STORAGE_KEY)).toBe(serialize(state));
    expect(load(storage)).toEqual(state);
  });
});
