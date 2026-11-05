import { createPinia } from "pinia";
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";

// 创建并装配持久化插件
const pinia = createPinia();

pinia.use(piniaPluginPersistedstate);

export default pinia;
