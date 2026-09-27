/** 应用状态 */
import { defineStore } from "pinia";
import { parse, serialize, type Storage } from "@app/state";

// localStorage 适配为状态包 Storage 接口
const stateStorage: Storage = {
  getItem: (key) => localStorage.getItem(key),
  setItem: (key, value) => localStorage.setItem(key, value),
};

/** 应用状态仓库：持久化接状态包 */
export const useAppStore = defineStore(
  "app",
  () => {
    return {};
  },
  {
    persist: {
      // 序列化
      serializer: {
        serialize: (state) => serialize(state as never),
        deserialize: (raw) => parse(raw) as never,
      },
      // 存储
      storage: stateStorage,
    },
  },
);
