/** 冒烟测试 */
import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import Home from "@/pages/home/index.vue";

describe("smoke", () => {
  it("首页渲染 wd 组件", () => {
    const wrapper = mount(Home, {
      global: { stubs: { "wd-button": true } },
    });

    expect(wrapper.html()).toContain("wd-button-stub");
  });
});
