/** 应用测试 */

import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import App from "@/App.vue";

describe("App", () => {
  it("渲染 RouterView", () => {
    const wrapper = mount(App, {
      global: { stubs: { RouterView: true } },
    });

    expect(wrapper.findComponent({ name: "RouterView" }).exists()).toBe(true);
  });
});
