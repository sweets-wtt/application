<script setup lang="ts">
// 嵌套布局
</script>

<template>
	<div class="min-h-screen flex flex-col">
		<!-- 顶部内容区 -->
		<header class="h-14 flex items-center px-4 border-b">
			<span class="font-bold">Application</span>
		</header>
		<!-- 主内容区 -->
		<main class="flex-1 p-4">
			<RouterView />
		</main>
	</div>
</template>
