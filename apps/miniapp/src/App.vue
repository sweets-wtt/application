<script setup lang="ts">
// 应用根组件
import { onHide, onLaunch, onShow } from "@/core/lifecycle";

// 启动
onLaunch(() => {});

// 前台
onShow(() => {});

// 后台
onHide(() => {});
</script>

<style lang="scss">
/* 全局样式 */
@use "./styles/main.scss";
</style>
