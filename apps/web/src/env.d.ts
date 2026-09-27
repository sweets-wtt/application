/// <reference types="vite/client" />

// .vue 模块声明
declare module "*.vue" {
  import type { DefineComponent } from "vue";
  const component: DefineComponent<Record<string, never>, Record<string, never>, unknown>;
  export default component;
}

// 环境变量类型
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_TELEMETRY_URL?: string;
  readonly VITE_OIDC_ISSUER?: string;
  readonly VITE_OIDC_CLIENT_ID?: string;
  readonly VITE_RELEASE?: string;
  readonly VITE_HEARTBEAT_INTERVAL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
