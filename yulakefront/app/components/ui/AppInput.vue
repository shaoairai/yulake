<template>
  <!-- 通用輸入框元件 -->
  <div class="app-input-wrapper">
    <!-- 標籤 -->
    <label v-if="label" :for="inputId" class="app-input__label">
      {{ label }}
      <span v-if="required" class="app-input__required">*</span>
    </label>

    <!-- 輸入框容器 -->
    <div
      :class="[
        'app-input__container',
        { 'app-input__container--focused': isFocused },
        { 'app-input__container--error': error },
        { 'app-input__container--disabled': disabled }
      ]"
    >
      <!-- 前置圖示 -->
      <span v-if="$slots.prefix" class="app-input__prefix">
        <slot name="prefix" />
      </span>

      <!-- 輸入框 -->
      <input
        :id="inputId"
        v-model="modelValue"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :autocomplete="autocomplete"
        class="app-input"
        @focus="isFocused = true"
        @blur="isFocused = false"
      >

      <!-- 後置圖示 -->
      <span v-if="$slots.suffix" class="app-input__suffix">
        <slot name="suffix" />
      </span>

      <!-- 清除按鈕 -->
      <button
        v-if="clearable && modelValue"
        type="button"
        class="app-input__clear"
        @click="handleClear"
      >
        ✕
      </button>
    </div>

    <!-- 提示文字 -->
    <p v-if="hint && !error" class="app-input__hint">{{ hint }}</p>

    <!-- 錯誤訊息 -->
    <p v-if="error" class="app-input__error">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
/**
 * AppInput - 通用輸入框元件
 * 支援多種輸入類型與狀態
 */
import { ref, computed } from 'vue'

// 定義 Props 型別
interface Props {
  /** v-model 綁定值 */
  modelValue?: string | number
  /** 輸入框標籤 */
  label?: string
  /** 輸入框類型 */
  type?: 'text' | 'password' | 'email' | 'number' | 'tel' | 'url' | 'search' | 'date' | 'time' | 'datetime-local'
  /** 佔位文字 */
  placeholder?: string
  /** 是否禁用 */
  disabled?: boolean
  /** 是否唯讀 */
  readonly?: boolean
  /** 是否必填 */
  required?: boolean
  /** 是否可清除 */
  clearable?: boolean
  /** 提示文字 */
  hint?: string
  /** 錯誤訊息 */
  error?: string
  /** 自動完成 */
  autocomplete?: string
}

// 定義 Props 預設值
const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  label: undefined,
  type: 'text',
  placeholder: '',
  disabled: false,
  readonly: false,
  required: false,
  clearable: false,
  hint: undefined,
  error: undefined,
  autocomplete: 'off'
})

// 定義事件
const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  clear: []
}>()

// 雙向綁定
const modelValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 聚焦狀態
const isFocused = ref(false)

// 產生唯一 ID
const inputId = computed(() => `input-${Math.random().toString(36).substring(2, 9)}`)

// 清除處理
const handleClear = () => {
  emit('update:modelValue', '')
  emit('clear')
}
</script>

<style scoped>
.app-input-wrapper {
  width: 100%;
}

.app-input__label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-primary);
}

.app-input__required {
  color: var(--color-error);
  margin-left: 2px;
}

.app-input__container {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  height: 40px;
  padding: 0 var(--spacing-sm);
  background-color: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.app-input__container--focused {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.app-input__container--error {
  border-color: var(--color-error);
}

.app-input__container--error.app-input__container--focused {
  box-shadow: 0 0 0 3px var(--color-error-light);
}

.app-input__container--disabled {
  background-color: var(--color-bg);
  cursor: not-allowed;
}

.app-input {
  flex: 1;
  height: 100%;
  border: none;
  background: transparent;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  outline: none;
}

.app-input::placeholder {
  color: var(--color-text-muted);
}

.app-input:disabled {
  cursor: not-allowed;
  color: var(--color-text-muted);
}

.app-input__prefix,
.app-input__suffix {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

.app-input__clear {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  padding: 0;
  border: none;
  background: var(--color-bg-hover);
  border-radius: var(--radius-full);
  color: var(--color-text-muted);
  font-size: 10px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.app-input__clear:hover {
  background: var(--color-border);
  color: var(--color-text-secondary);
}

.app-input__hint {
  margin: var(--spacing-xs) 0 0 0;
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.app-input__error {
  margin: var(--spacing-xs) 0 0 0;
  font-size: var(--font-size-xs);
  color: var(--color-error);
}
</style>
