<template>
  <!-- 統計數字卡片元件 -->
  <div class="admin-stat-card">
    <!-- 圖示區塊 -->
    <div
      v-if="icon"
      :class="['admin-stat-card__icon', `admin-stat-card__icon--${variant}`]"
    >
      {{ icon }}
    </div>

    <!-- 內容區塊 -->
    <div class="admin-stat-card__content">
      <span class="admin-stat-card__title">{{ title }}</span>
      <span class="admin-stat-card__value">{{ formattedValue }}</span>
      <span
        v-if="subtitle"
        :class="[
          'admin-stat-card__subtitle',
          { 'admin-stat-card__subtitle--positive': isPositive },
          { 'admin-stat-card__subtitle--negative': isNegative }
        ]"
      >
        {{ subtitle }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * AdminStatCard - 統計數字卡片元件
 * 用於 Dashboard 顯示關鍵數據指標
 */
import { computed } from 'vue'

// 定義 Props 型別
interface Props {
  /** 卡片標題 */
  title: string
  /** 數值 */
  value: string | number
  /** 副標題（例如：較上週 +12%） */
  subtitle?: string
  /** 圖示 */
  icon?: string
  /** 樣式變體 */
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'error'
}

// 定義 Props 預設值
const props = withDefaults(defineProps<Props>(), {
  subtitle: undefined,
  icon: undefined,
  variant: 'default'
})

// 格式化數值（數字加入千分位）
const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    return props.value.toLocaleString()
  }
  return props.value
})

// 判斷副標題是否為正向成長
const isPositive = computed(() => {
  return props.subtitle?.includes('+')
})

// 判斷副標題是否為負向
const isNegative = computed(() => {
  return props.subtitle?.includes('-') && !props.subtitle?.includes('爽約')
})
</script>

<style scoped>
.admin-stat-card {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background-color: var(--color-bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

/* 圖示區塊 */
.admin-stat-card__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  font-size: var(--font-size-xl);
  flex-shrink: 0;
}

.admin-stat-card__icon--default {
  background-color: var(--color-bg-hover);
}

.admin-stat-card__icon--primary {
  background-color: var(--color-primary-light);
}

.admin-stat-card__icon--success {
  background-color: var(--color-success-light);
}

.admin-stat-card__icon--warning {
  background-color: var(--color-warning-light);
}

.admin-stat-card__icon--error {
  background-color: var(--color-error-light);
}

/* 內容區塊 */
.admin-stat-card__content {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.admin-stat-card__title {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.admin-stat-card__value {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: var(--line-height-tight);
}

.admin-stat-card__subtitle {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.admin-stat-card__subtitle--positive {
  color: var(--color-success);
}

.admin-stat-card__subtitle--negative {
  color: var(--color-error);
}
</style>
