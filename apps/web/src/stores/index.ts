/** 状态管理 */
import { createPinia } from "pinia";
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";

// Pinia 实例
export const pinia = createPinia();

// 持久化插件
pinia.use(piniaPluginPersistedstate);
