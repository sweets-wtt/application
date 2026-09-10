/** 应用状态 */
import { parse, type State, serialize } from "@app/state";
import { defineStore } from "pinia";

export const useAppStore = defineStore(
  "app",
  () => {
    return {};
  },
  {
    persist: {
      // 序列化接
      serializer: {
        deserialize: (data: string) => parse(data),
        serialize: (data) => serialize(data as State),
      },
    },
  },
);
