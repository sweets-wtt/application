/** 状态管理 */

import * as Pinia from "pinia";
import { createPersistedState } from "pinia-plugin-persistedstate";

export { Pinia };

// Pinia 实例
export const pinia = Pinia.createPinia();

// 持久化插件：storage 接 uni
pinia.use(
  createPersistedState({
    storage: {
      getItem: uni.getStorageSync,
      setItem: uni.setStorageSync,
    },
  }),
);
