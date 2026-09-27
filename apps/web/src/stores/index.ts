/** Pinia 实例 */
import { createPinia } from "pinia";
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";

// 创建并装配持久化插件
export const pinia = createPinia();

pinia.use(piniaPluginPersistedstate);
