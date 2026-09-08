/** 状态测试 */
import { describe, expect, it } from "vitest";
import { defaultState, load, parse, STORAGE_KEY, type State, save, serialize } from "../src/index";

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

  it("非法数据回退默认状态", () => {
    expect(parse('{"version":"9"}')).toEqual(defaultState);
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
