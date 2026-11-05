import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import App from "@/App.vue";

describe("app", () => {
  it("渲染根组件", () => {
    const wrapper = mount(App);

    expect(wrapper.exists()).toBe(true);
  });
});
