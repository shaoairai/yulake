<template>
  <!-- 通用 Modal 對話框元件 -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" class="app-modal-overlay" @click="handleOverlayClick">
        <div
          :class="[
            'app-modal',
            `app-modal--${size}`
          ]"
          @click.stop
        >
          <!-- Modal 標題區 -->
          <div class="app-modal__header">
            <h3 class="app-modal__title">{{ title }}</h3>
            <button
              v-if="closable"
              type="button"
              class="app-modal__close"
              @click="close"
            >
              ✕
            </button>
          </div>

          <!-- Modal 內容區 -->
          <div class="app-modal__body">
            <slot />
          </div>

          <!-- Modal 底部區 -->
          <div v-if="$slots.footer" class="app-modal__footer">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
/**
 * AppModal - 通用 Modal 對話框元件
 * 支援多種大小與自訂內容
 */
import { watch } from 'vue'

// 定義 Props 型別
interface Props {
  /** v-model 控制顯示/隱藏 */
  modelValue: boolean
  /** Modal 標題 */
  title: string
  /** Modal 大小 */
  size?: 'sm' | 'md' | 'lg' | 'xl'
  /** 是否顯示關閉按鈕 */
  closable?: boolean
  /** 點擊遮罩是否關閉 */
  closeOnOverlay?: boolean
}

// 定義 Props 預設值
const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  closable: true,
  closeOnOverlay: true
})

// 定義事件
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  close: []
}>()

// 關閉 Modal
const close = () => {
  emit('update:modelValue', false)
  emit('close')
}

// 點擊遮罩處理
const handleOverlayClick = () => {
  if (props.closeOnOverlay) {
    close()
  }
}

// 監聽開啟狀態，控制 body 滾動
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})
</script>

<style scoped>
.app-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(2px);
}

.app-modal {
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 48px);
  background-color: var(--color-bg-card);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

/* 大小變體 */
.app-modal--sm {
  width: 100%;
  max-width: 400px;
}

.app-modal--md {
  width: 100%;
  max-width: 500px;
}

.app-modal--lg {
  width: 100%;
  max-width: 680px;
}

.app-modal--xl {
  width: 100%;
  max-width: 900px;
}

.app-modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.app-modal__title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.app-modal__close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  border: none;
  background: transparent;
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  font-size: 14px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.app-modal__close:hover {
  background-color: var(--color-bg-hover);
  color: var(--color-text-primary);
}

.app-modal__body {
  flex: 1;
  padding: var(--spacing-lg);
  overflow-y: auto;
}

.app-modal__footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  border-top: 1px solid var(--color-border-light);
  background-color: var(--color-bg);
}

/* 動畫效果 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-active .app-modal,
.modal-leave-active .app-modal {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .app-modal,
.modal-leave-to .app-modal {
  transform: scale(0.95);
  opacity: 0;
}
</style>
