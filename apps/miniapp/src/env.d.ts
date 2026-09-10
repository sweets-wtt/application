/** Vite 客户端类型 */
/// <reference types="vite/client" />

/** Vue 单文件组件 */
declare module "*.vue" {
  import type { DefineComponent } from "vue";

  const component: DefineComponent<Record<string, never>, Record<string, never>, unknown>;

  export default component;
}
