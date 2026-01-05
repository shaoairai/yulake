<template>
  <!-- 通用按鈕元件 -->
  <button
    :class="[
      'app-button',
      `app-button--${variant}`,
      `app-button--${size}`,
      { 'app-button--block': block },
      { 'app-button--loading': loading },
      { 'app-button--disabled': disabled }
    ]"
    :disabled="disabled || loading"
    :type="type"
    @click="handleClick"
  >
    <!-- 載入中圖示 -->
    <span v-if="loading" class="app-button__spinner">
      <span class="spinner"></span>
    </span>
    <!-- 前置圖示插槽 -->
    <span v-if="$slots.icon && !loading" class="app-button__icon">
      <slot name="icon" />
    </span>
    <!-- 按鈕文字 -->
    <span class="app-button__text">
      <slot />
    </span>
  </button>
</template>

<script setup lang="ts">
/**
 * AppButton - 通用按鈕元件
 * 支援多種樣式變體、大小與狀態
 */

// 定義 Props 型別
interface Props {
  /** 按鈕樣式變體 */
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  /** 按鈕大小 */
  size?: 'sm' | 'md' | 'lg'
  /** 按鈕類型 */
  type?: 'button' | 'submit' | 'reset'
  /** 是否為區塊級按鈕（100%寬度） */
  block?: boolean
  /** 是否禁用 */
  disabled?: boolean
  /** 是否顯示載入狀態 */
  loading?: boolean
}

// 定義 Props 預設值
const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  type: 'button',
  block: false,
  disabled: false,
  loading: false
})

// 定義事件
const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

// 點擊處理
const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped>
.app-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
  text-decoration: none;
}

/* 大小變體 */
.app-button--sm {
  height: 32px;
  padding: 0 var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.app-button--md {
  height: 40px;
  padding: 0 var(--spacing-md);
  font-size: var(--font-size-sm);
}

.app-button--lg {
  height: 48px;
  padding: 0 var(--spacing-lg);
  font-size: var(--font-size-base);
}

/* 樣式變體 - Primary */
.app-button--primary {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  border-color: var(--color-primary);
}

.app-button--primary:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
}

/* 樣式變體 - Secondary */
.app-button--secondary {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  border-color: var(--color-primary-light);
}

.app-button--secondary:hover:not(:disabled) {
  background-color: var(--color-secondary);
  border-color: var(--color-secondary);
}

/* 樣式變體 - Outline */
.app-button--outline {
  background-color: transparent;
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.app-button--outline:hover:not(:disabled) {
  background-color: var(--color-primary-light);
}

/* 樣式變體 - Ghost */
.app-button--ghost {
  background-color: transparent;
  color: var(--color-text-secondary);
  border-color: transparent;
}

.app-button--ghost:hover:not(:disabled) {
  background-color: var(--color-bg-hover);
  color: var(--color-text-primary);
}

/* 樣式變體 - Danger */
.app-button--danger {
  background-color: var(--color-error);
  color: var(--color-text-inverse);
  border-color: var(--color-error);
}

.app-button--danger:hover:not(:disabled) {
  background-color: #DC2626;
  border-color: #DC2626;
}

/* 區塊級按鈕 */
.app-button--block {
  display: flex;
  width: 100%;
}

/* 禁用狀態 */
.app-button--disabled,
.app-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 載入狀態 */
.app-button--loading {
  cursor: wait;
}

.app-button__spinner {
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 圖示 */
.app-button__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1em;
}
</style>
