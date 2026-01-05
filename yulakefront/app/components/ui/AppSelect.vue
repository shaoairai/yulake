<template>
  <!-- 通用下拉選單元件 -->
  <div class="app-select-wrapper">
    <!-- 標籤 -->
    <label v-if="label" :for="selectId" class="app-select__label">
      {{ label }}
      <span v-if="required" class="app-select__required">*</span>
    </label>

    <!-- 選單容器 -->
    <div
      :class="[
        'app-select__container',
        { 'app-select__container--focused': isFocused },
        { 'app-select__container--error': error },
        { 'app-select__container--disabled': disabled }
      ]"
    >
      <select
        :id="selectId"
        v-model="modelValue"
        :disabled="disabled"
        class="app-select"
        @focus="isFocused = true"
        @blur="isFocused = false"
      >
        <!-- 預設選項 -->
        <option v-if="placeholder" value="" disabled>
          {{ placeholder }}
        </option>
        <!-- 選項列表 -->
        <option
          v-for="option in options"
          :key="getOptionValue(option)"
          :value="getOptionValue(option)"
        >
          {{ getOptionLabel(option) }}
        </option>
      </select>

      <!-- 下拉箭頭 -->
      <span class="app-select__arrow">▼</span>
    </div>

    <!-- 提示文字 -->
    <p v-if="hint && !error" class="app-select__hint">{{ hint }}</p>

    <!-- 錯誤訊息 -->
    <p v-if="error" class="app-select__error">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
/**
 * AppSelect - 通用下拉選單元件
 * 支援物件陣列或簡單陣列作為選項
 */
import { ref, computed } from 'vue'

// 選項型別
type OptionType = string | number | { label: string; value: string | number }

// 定義 Props 型別
interface Props {
  /** v-model 綁定值 */
  modelValue?: string | number
  /** 選單標籤 */
  label?: string
  /** 選項陣列 */
  options: OptionType[]
  /** 佔位文字 */
  placeholder?: string
  /** 是否禁用 */
  disabled?: boolean
  /** 是否必填 */
  required?: boolean
  /** 提示文字 */
  hint?: string
  /** 錯誤訊息 */
  error?: string
  /** 自訂 label 欄位名稱 */
  labelKey?: string
  /** 自訂 value 欄位名稱 */
  valueKey?: string
}

// 定義 Props 預設值
const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  label: undefined,
  placeholder: undefined,
  disabled: false,
  required: false,
  hint: undefined,
  error: undefined,
  labelKey: 'label',
  valueKey: 'value'
})

// 定義事件
const emit = defineEmits<{
  'update:modelValue': [value: string | number]
}>()

// 雙向綁定
const modelValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 聚焦狀態
const isFocused = ref(false)

// 產生唯一 ID
const selectId = computed(() => `select-${Math.random().toString(36).substring(2, 9)}`)

// 取得選項值
const getOptionValue = (option: OptionType): string | number => {
  if (typeof option === 'object') {
    return option[props.valueKey as keyof typeof option] as string | number
  }
  return option
}

// 取得選項標籤
const getOptionLabel = (option: OptionType): string => {
  if (typeof option === 'object') {
    return option[props.labelKey as keyof typeof option] as string
  }
  return String(option)
}
</script>

<style scoped>
.app-select-wrapper {
  width: 100%;
}

.app-select__label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-primary);
}

.app-select__required {
  color: var(--color-error);
  margin-left: 2px;
}

.app-select__container {
  position: relative;
  display: flex;
  align-items: center;
  height: 40px;
  background-color: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.app-select__container--focused {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.app-select__container--error {
  border-color: var(--color-error);
}

.app-select__container--error.app-select__container--focused {
  box-shadow: 0 0 0 3px var(--color-error-light);
}

.app-select__container--disabled {
  background-color: var(--color-bg);
  cursor: not-allowed;
}

.app-select {
  width: 100%;
  height: 100%;
  padding: 0 var(--spacing-xl) 0 var(--spacing-sm);
  border: none;
  background: transparent;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  cursor: pointer;
  outline: none;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
}

.app-select:disabled {
  cursor: not-allowed;
  color: var(--color-text-muted);
}

.app-select__arrow {
  position: absolute;
  right: var(--spacing-sm);
  font-size: 10px;
  color: var(--color-text-muted);
  pointer-events: none;
}

.app-select__hint {
  margin: var(--spacing-xs) 0 0 0;
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.app-select__error {
  margin: var(--spacing-xs) 0 0 0;
  font-size: var(--font-size-xs);
  color: var(--color-error);
}
</style>
