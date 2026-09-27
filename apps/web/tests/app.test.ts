/** 应用组件测试 */
import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import App from "../src/App.vue";

describe("App", () => {
  it("渲染根组件", () => {
    const wrapper = mount(App);

    expect(wrapper.exists()).toBe(true);
  });
});
