<template>
  <!-- 確認預約頁面 -->
  <div class="booking-page" :style="themeStyle">
    <!-- 進度指示器 -->
    <div class="booking-progress">
      <div class="progress-step completed">
        <span class="step-number">✓</span>
        <span class="step-label">選擇服務</span>
      </div>
      <div class="progress-line completed" />
      <div class="progress-step completed">
        <span class="step-number">✓</span>
        <span class="step-label">選擇設計師</span>
      </div>
      <div class="progress-line completed" />
      <div class="progress-step completed">
        <span class="step-number">✓</span>
        <span class="step-label">選擇時間</span>
      </div>
      <div class="progress-line completed" />
      <div class="progress-step active">
        <span class="step-number">4</span>
        <span class="step-label">確認預約</span>
      </div>
    </div>

    <!-- Header -->
    <header class="salon-header">
      <button class="back-btn" @click="goBack">
        <span class="back-icon">←</span>
        <span>返回選擇時間</span>
      </button>
    </header>

    <!-- 預約摘要 -->
    <div class="booking-summary">
      <h2 class="section-title">預約資訊確認</h2>

      <div class="summary-card">
        <!-- 店家 -->
        <div class="summary-item">
          <span class="summary-icon">🏪</span>
          <div class="summary-content">
            <span class="summary-label">店家</span>
            <span class="summary-value">{{ bookingStore.salon?.name }}</span>
          </div>
        </div>

        <!-- 服務 -->
        <div class="summary-item">
          <span class="summary-icon">✨</span>
          <div class="summary-content">
            <span class="summary-label">服務項目</span>
            <span class="summary-value">{{ bookingStore.selectedService?.name }}</span>
          </div>
          <span class="summary-price">${{ bookingStore.selectedService?.price }}</span>
        </div>

        <!-- 設計師 -->
        <div class="summary-item">
          <span class="summary-icon">💇</span>
          <div class="summary-content">
            <span class="summary-label">設計師</span>
            <span class="summary-value">{{ bookingStore.selectedStylist?.name }}</span>
          </div>
        </div>

        <!-- 日期時間 -->
        <div class="summary-item">
          <span class="summary-icon">📅</span>
          <div class="summary-content">
            <span class="summary-label">預約時間</span>
            <span class="summary-value">{{ formattedDateTime }}</span>
          </div>
        </div>

        <!-- 預估時長 -->
        <div class="summary-item">
          <span class="summary-icon">⏱️</span>
          <div class="summary-content">
            <span class="summary-label">預估時長</span>
            <span class="summary-value">{{ bookingStore.selectedService?.duration }} 分鐘</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 顧客備註 -->
    <div class="note-section">
      <h2 class="section-title">備註（選填）</h2>
      <textarea
        v-model="customerNote"
        class="note-input"
        placeholder="有任何特殊需求或想說的話嗎？"
        rows="3"
        maxlength="500"
      />
      <span class="note-count">{{ customerNote.length }}/500</span>
    </div>

    <!-- 登入提示 -->
    <div v-if="!isAuthenticated" class="login-prompt">
      <p>您需要登入才能完成預約</p>
      <button class="login-btn" @click="goToLogin">登入 / 註冊</button>
    </div>

    <!-- 錯誤訊息 -->
    <div v-if="submitError" class="error-message">
      {{ submitError }}
    </div>

    <!-- 底部按鈕 -->
    <div class="booking-footer">
      <div class="total-row">
        <span class="total-label">總計</span>
        <span class="total-price">${{ bookingStore.selectedService?.price }}</span>
      </div>
      <button
        class="submit-btn"
        :disabled="!canSubmit || submitting"
        @click="submitBooking"
      >
        <span v-if="submitting" class="btn-loading" />
        <span v-else>確認預約</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 預約流程 Step 4：確認預約
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBookingApi } from '~/composables/useBookingApi'
import { useBookingStore } from '~/stores/booking'
import { useAuth } from '~/composables/useAuth'

// 路由
const route = useRoute()
const router = useRouter()
const code = computed(() => route.params.code as string)

// API、Store 與 Auth
const bookingApi = useBookingApi()
const bookingStore = useBookingStore()
const { isAuthenticated } = useAuth()

// 狀態
const customerNote = ref('')
const submitting = ref(false)
const submitError = ref('')

// 主題樣式
const themeStyle = computed(() => {
  if (!bookingStore.salon?.theme_color) return {}
  return {
    '--theme-color': bookingStore.salon.theme_color,
    '--theme-color-light': `${bookingStore.salon.theme_color}15`,
    '--theme-color-dark': bookingStore.salon.theme_color
  }
})

// 格式化日期時間
const formattedDateTime = computed(() => {
  if (!bookingStore.selectedDate || !bookingStore.selectedTime) return ''

  const date = new Date(bookingStore.selectedDate)
  const weekdays = ['週日', '週一', '週二', '週三', '週四', '週五', '週六']

  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  const weekday = weekdays[date.getDay()]

  return `${year}/${month}/${day} (${weekday}) ${bookingStore.selectedTime}`
})

// 是否可以提交
const canSubmit = computed(() => {
  return isAuthenticated.value &&
    bookingStore.selectedService &&
    bookingStore.selectedStylist &&
    bookingStore.selectedDate &&
    bookingStore.selectedTime
})

// 返回上一步
const goBack = () => {
  router.push(`/s/${code.value}/booking/time`)
}

// 前往登入
const goToLogin = () => {
  // 儲存當前路徑，登入後返回
  sessionStorage.setItem('redirectAfterLogin', route.fullPath)
  router.push('/auth/login')
}

// 提交預約
const submitBooking = async () => {
  if (!canSubmit.value) return

  submitting.value = true
  submitError.value = ''

  try {
    const res = await bookingApi.createBooking({
      salon_code: code.value,
      service_id: bookingStore.selectedService!.id,
      stylist_id: bookingStore.selectedStylist!.id,
      booking_date: bookingStore.selectedDate,
      start_time: bookingStore.selectedTime,
      customer_note: customerNote.value || undefined
    })

    if (res.success && res.data) {
      // 清除預約狀態
      bookingStore.reset()

      // 導向成功頁面
      router.push({
        path: `/s/${code.value}/booking/success`,
        query: { id: res.data.id }
      })
    } else {
      submitError.value = res.error || '預約失敗，請稍後再試'
    }
  } catch (e) {
    console.error('Failed to create booking:', e)
    submitError.value = '預約失敗，請稍後再試'
  } finally {
    submitting.value = false
  }
}

// 初始化
onMounted(() => {
  // 檢查前置條件
  if (!bookingStore.canConfirm) {
    router.push(`/s/${code.value}/booking`)
    return
  }

  // 恢復備註
  if (bookingStore.customerNote) {
    customerNote.value = bookingStore.customerNote
  }
})
</script>

<style scoped>
.booking-page {
  --theme-color: var(--color-primary);
  --theme-color-light: var(--color-primary-light);
  --theme-color-dark: var(--color-primary-dark);

  min-height: 100vh;
  background-color: var(--color-bg);
  padding-bottom: 140px;
}

/* 進度指示器 */
.booking-progress {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg) var(--spacing-md);
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border-light);
  gap: var(--spacing-xs);
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.step-number {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: var(--font-size-sm);
  font-weight: 600;
  background: var(--color-border);
  color: var(--color-text-muted);
}

.progress-step.active .step-number {
  background: var(--theme-color);
  color: white;
}

.progress-step.completed .step-number {
  background: var(--color-success);
  color: white;
}

.step-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  white-space: nowrap;
}

.progress-step.active .step-label {
  color: var(--theme-color);
  font-weight: 500;
}

.progress-line {
  width: 20px;
  height: 2px;
  background: var(--color-border);
  margin-bottom: 20px;
}

.progress-line.completed {
  background: var(--color-success);
}

/* Header */
.salon-header {
  padding: var(--spacing-md);
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border-light);
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  color: var(--theme-color);
  background: none;
  border: none;
  font-size: var(--font-size-sm);
  font-weight: 500;
  cursor: pointer;
  padding: 0;
}

.back-icon {
  font-size: 18px;
}

/* 預約摘要 */
.booking-summary {
  padding: var(--spacing-lg);
}

.section-title {
  font-size: var(--font-size-md);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-md) 0;
}

.summary-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
}

.summary-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) 0;
}

.summary-item:not(:last-child) {
  border-bottom: 1px solid var(--color-border-light);
}

.summary-icon {
  font-size: 24px;
  width: 32px;
  text-align: center;
}

.summary-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.summary-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.summary-value {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  font-weight: 500;
}

.summary-price {
  font-size: var(--font-size-md);
  color: var(--theme-color);
  font-weight: 600;
}

/* 備註 */
.note-section {
  padding: 0 var(--spacing-lg) var(--spacing-lg);
}

.note-input {
  width: 100%;
  padding: var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-family: inherit;
  resize: none;
  background: var(--color-bg-card);
}

.note-input:focus {
  outline: none;
  border-color: var(--theme-color);
}

.note-count {
  display: block;
  text-align: right;
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  margin-top: var(--spacing-xs);
}

/* 登入提示 */
.login-prompt {
  margin: 0 var(--spacing-lg);
  padding: var(--spacing-lg);
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  text-align: center;
  border: 1px solid var(--color-warning);
}

.login-prompt p {
  margin: 0 0 var(--spacing-md) 0;
  color: var(--color-text-secondary);
}

.login-btn {
  padding: var(--spacing-sm) var(--spacing-xl);
  background: var(--theme-color);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: 500;
  cursor: pointer;
}

/* 錯誤訊息 */
.error-message {
  margin: var(--spacing-md) var(--spacing-lg);
  padding: var(--spacing-md);
  background: var(--color-error-light);
  border: 1px solid var(--color-error);
  border-radius: var(--radius-md);
  color: var(--color-error);
  font-size: var(--font-size-sm);
  text-align: center;
}

/* 底部按鈕 */
.booking-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: var(--spacing-md);
  background: var(--color-bg-card);
  border-top: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-lg);
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.total-label {
  font-size: var(--font-size-md);
  color: var(--color-text-primary);
}

.total-price {
  font-size: var(--font-size-xl);
  color: var(--theme-color);
  font-weight: 700;
}

.submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  padding: var(--spacing-md);
  background: var(--theme-color);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  font-size: var(--font-size-md);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  min-height: 48px;
}

.submit-btn:disabled {
  background: var(--color-border);
  cursor: not-allowed;
}

.submit-btn:not(:disabled):hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.btn-loading {
  width: 20px;
  height: 20px;
  border: 2px solid white;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
