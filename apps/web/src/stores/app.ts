import { defineStore } from "pinia";

import { type Storage, parseState, serializeState } from "@/lib/storage";

// LocalStorage 适配为状态包 Storage 接口
const stateStorage: Storage = {
  getItem: (key) => localStorage.getItem(key),
  setItem: (key, value) => localStorage.setItem(key, value),
};

/** 应用状态仓库：持久化接状态包 */
const useAppStore = defineStore("app", () => ({}), {
  persist: {
    // 序列化
    serializer: {
      deserialize: (raw) => parseState(raw) as never,
      serialize: (state) => serializeState(state as never),
    },
    // 存储
    storage: stateStorage,
  },
});

export default useAppStore;
