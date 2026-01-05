<template>
  <!-- 預設 Layout（使用者前台） -->
  <div class="default-layout">
    <main class="default-layout__main">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
/**
 * Default Layout - 預設版面配置
 * 用於使用者前台頁面（非 admin）
 */
</script>

<style scoped>
.default-layout {
  min-height: 100vh;
  background-color: var(--color-bg);
}

.default-layout__main {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-lg);
}
</style>
