import { parseState, serializeState } from "@/lib/storage";

import type { Storage } from "@/lib/storage";

/** LocalStorage 适配为 Storage 接口 */
const stateStorage: Storage = {
  getItem: (key) => localStorage.getItem(key),
  setItem: (key, value) => localStorage.setItem(key, value),
};

/** 应用状态仓库：空实现，仅接入持久化 */
const useAppStore = defineStore("app", () => ({}), {
  persist: {
    // 反序列化时按版本迁移
    serializer: {
      deserialize: (raw) => parseState(raw) as never,
      serialize: (state) => serializeState(state as never),
    },
    // 使用本地存储
    storage: stateStorage,
  },
});

export default useAppStore;
