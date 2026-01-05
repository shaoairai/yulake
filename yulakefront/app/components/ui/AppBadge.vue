<template>
  <!-- 通用徽章/標籤元件 -->
  <span
    :class="[
      'app-badge',
      `app-badge--${variant}`,
      `app-badge--${size}`
    ]"
  >
    <!-- 圓點指示器 -->
    <span v-if="dot" class="app-badge__dot"></span>
    <!-- 徽章內容 -->
    <slot />
  </span>
</template>

<script setup lang="ts">
/**
 * AppBadge - 通用徽章/標籤元件
 * 用於顯示狀態、分類或數量
 */

// 定義 Props 型別
interface Props {
  /** 徽章樣式變體 */
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'error' | 'info'
  /** 徽章大小 */
  size?: 'sm' | 'md'
  /** 是否顯示圓點指示器 */
  dot?: boolean
}

// 定義 Props 預設值
withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'md',
  dot: false
})
</script>

<style scoped>
.app-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-weight: 500;
  border-radius: var(--radius-full);
  white-space: nowrap;
}

/* 大小變體 */
.app-badge--sm {
  padding: 2px 8px;
  font-size: var(--font-size-xs);
}

.app-badge--md {
  padding: 4px 12px;
  font-size: var(--font-size-sm);
}

/* 樣式變體 - Default */
.app-badge--default {
  background-color: var(--color-bg-hover);
  color: var(--color-text-secondary);
}

/* 樣式變體 - Primary */
.app-badge--primary {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

/* 樣式變體 - Success */
.app-badge--success {
  background-color: var(--color-success-light);
  color: var(--color-success);
}

/* 樣式變體 - Warning */
.app-badge--warning {
  background-color: var(--color-warning-light);
  color: #B45309;
}

/* 樣式變體 - Error */
.app-badge--error {
  background-color: var(--color-error-light);
  color: var(--color-error);
}

/* 樣式變體 - Info */
.app-badge--info {
  background-color: var(--color-info-light);
  color: var(--color-info);
}

/* 圓點指示器 */
.app-badge__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: currentColor;
}
</style>
