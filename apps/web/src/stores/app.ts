import { defineStore } from "pinia";

import { parseState, serializeState } from "@/lib/storage";

import type { StorageLike } from "pinia-plugin-persistedstate";

/** LocalStorage 适配为插件存储接口 */
const stateStorage: StorageLike = {
  getItem: (key) => localStorage.getItem(key),
  setItem: (key, value) => {
    localStorage.setItem(key, value);
  },
};

/** 应用状态仓库：空实现，仅接入持久化 */
const useAppStore = defineStore("app", () => ({}), {
  persist: {
    // 反序列化时按版本迁移
    serializer: {
      deserialize: (raw) => parseState(raw),
      // 序列化入口为无约束状态树，直接透传
      serialize: (state: Readonly<Record<PropertyKey, unknown>>) => serializeState(state),
    },
    // 使用本地存储
    storage: stateStorage,
  },
});

export default useAppStore;
