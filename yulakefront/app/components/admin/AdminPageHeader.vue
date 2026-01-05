<template>
  <!-- 後台頁面標題區元件 -->
  <div class="admin-page-header">
    <div class="admin-page-header__content">
      <!-- 標題 -->
      <h1 class="admin-page-header__title">{{ title }}</h1>
      <!-- 說明文字 -->
      <p v-if="description" class="admin-page-header__description">
        {{ description }}
      </p>
    </div>

    <!-- 操作按鈕區（透過 slot） -->
    <div v-if="$slots.actions" class="admin-page-header__actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * AdminPageHeader - 後台頁面標題區元件
 * 用於每個後台頁面最上方顯示標題與操作按鈕
 */

// 定義 Props 型別
interface Props {
  /** 頁面標題 */
  title: string
  /** 頁面說明 */
  description?: string
}

// 定義 Props 預設值
withDefaults(defineProps<Props>(), {
  description: undefined
})
</script>

<style scoped>
.admin-page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

.admin-page-header__content {
  flex: 1;
  min-width: 0;
}

.admin-page-header__title {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.admin-page-header__description {
  margin: var(--spacing-xs) 0 0 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.admin-page-header__actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-shrink: 0;
}

/* 響應式：小螢幕 */
@media (max-width: 768px) {
  .admin-page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .admin-page-header__actions {
    justify-content: flex-start;
  }
}
</style>
