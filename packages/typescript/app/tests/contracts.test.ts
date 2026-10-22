import { expect, it } from "vitest";
import { appFetch } from "../src/contracts/client";
import * as contracts from "../src/contracts";
import * as msw from "../src/contracts/msw";

it("mutator 为函数", () => {
  expect(typeof appFetch).toBe("function");
});

it("契约 barrel 可加载", () => {
  expect(contracts).not.toBeNull();
});

it("模拟钩子 barrel 可加载", () => {
  expect(msw).not.toBeNull();
});
