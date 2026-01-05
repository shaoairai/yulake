<template>
  <!-- 通用卡片元件 -->
  <div
    :class="[
      'app-card',
      { 'app-card--hoverable': hoverable },
      { 'app-card--bordered': bordered },
      { 'app-card--no-padding': noPadding }
    ]"
  >
    <!-- 卡片標題區 -->
    <div v-if="title || $slots.header" class="app-card__header">
      <div class="app-card__header-content">
        <h3 v-if="title" class="app-card__title">{{ title }}</h3>
        <p v-if="subtitle" class="app-card__subtitle">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.headerAction" class="app-card__header-action">
        <slot name="headerAction" />
      </div>
      <!-- 自訂標題區插槽 -->
      <slot name="header" />
    </div>

    <!-- 卡片內容區 -->
    <div class="app-card__body">
      <slot />
    </div>

    <!-- 卡片底部區 -->
    <div v-if="$slots.footer" class="app-card__footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * AppCard - 通用卡片元件
 * 用於包裝內容區塊，提供統一的視覺樣式
 */

// 定義 Props 型別
interface Props {
  /** 卡片標題 */
  title?: string
  /** 卡片副標題 */
  subtitle?: string
  /** 是否有 hover 效果 */
  hoverable?: boolean
  /** 是否顯示邊框 */
  bordered?: boolean
  /** 是否移除內距 */
  noPadding?: boolean
}

// 定義 Props 預設值
withDefaults(defineProps<Props>(), {
  title: undefined,
  subtitle: undefined,
  hoverable: false,
  bordered: false,
  noPadding: false
})
</script>

<style scoped>
.app-card {
  background-color: var(--color-bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.app-card--hoverable {
  transition: box-shadow var(--transition-fast), transform var(--transition-fast);
  cursor: pointer;
}

.app-card--hoverable:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.app-card--bordered {
  border: 1px solid var(--color-border);
  box-shadow: none;
}

.app-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.app-card__header-content {
  flex: 1;
}

.app-card__title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.app-card__subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: var(--spacing-xs) 0 0 0;
}

.app-card__header-action {
  flex-shrink: 0;
  margin-left: var(--spacing-md);
}

.app-card__body {
  padding: var(--spacing-lg);
}

.app-card--no-padding .app-card__body {
  padding: 0;
}

.app-card__footer {
  padding: var(--spacing-md) var(--spacing-lg);
  border-top: 1px solid var(--color-border-light);
  background-color: var(--color-bg);
}
</style>
