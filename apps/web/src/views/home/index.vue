<script setup lang="ts">
// 首页视图
import { computed } from "vue";
import { useHealthCheck } from "@/features/health/useHealthCheck";

const { status } = useHealthCheck();

// 状态样式
const statusClass = computed(() => {
  switch (status.value) {
    case "online":
      return "bg-green-500";
    case "offline":
      return "bg-red-500";
    default:
      return "bg-gray-400 animate-pulse";
  }
});

// 状态文案
const statusText = computed(() => {
  switch (status.value) {
    case "online":
      return "服务端在线";
    case "offline":
      return "服务端离线";
    default:
      return "连接中...";
  }
});
</script>

<template>
  <div class="p-4">
    <h1 class="text-2xl font-bold">首页</h1>

    <!-- 服务端状态 -->
    <div class="mt-4 flex items-center gap-2">
      <span class="inline-block h-2.5 w-2.5 rounded-full" :class="statusClass" />
      <span class="text-sm text-gray-600">{{ statusText }}</span>
    </div>
  </div>
</template>
