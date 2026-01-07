<template>
  <!-- 選擇時間頁面 -->
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
      <div class="progress-step active">
        <span class="step-number">3</span>
        <span class="step-label">選擇時間</span>
      </div>
      <div class="progress-line" />
      <div class="progress-step">
        <span class="step-number">4</span>
        <span class="step-label">確認預約</span>
      </div>
    </div>

    <!-- Header -->
    <header class="salon-header">
      <button class="back-btn" @click="goBack">
        <span class="back-icon">←</span>
        <span>返回選擇設計師</span>
      </button>
    </header>

    <!-- 已選擇的資訊 -->
    <div class="selected-info">
      <div v-if="bookingStore.selectedService" class="info-row">
        <span class="info-label">服務：</span>
        <span class="info-value">{{ bookingStore.selectedService.name }}</span>
      </div>
      <div v-if="bookingStore.selectedStylist" class="info-row">
        <span class="info-label">設計師：</span>
        <span class="info-value">{{ bookingStore.selectedStylist.name }}</span>
      </div>
    </div>

    <!-- 日期選擇 -->
    <div class="date-section">
      <h2 class="section-title">選擇日期</h2>
      <div class="date-picker">
        <button
          v-for="dateOption in dateOptions"
          :key="dateOption.value"
          class="date-btn"
          :class="{ 'date-btn--selected': selectedDate === dateOption.value }"
          @click="selectDate(dateOption.value)"
        >
          <span class="date-weekday">{{ dateOption.weekday }}</span>
          <span class="date-day">{{ dateOption.day }}</span>
          <span class="date-month">{{ dateOption.month }}</span>
        </button>
      </div>
    </div>

    <!-- 時段選擇 -->
    <div v-if="selectedDate" class="time-section">
      <h2 class="section-title">選擇時段</h2>

      <div v-if="loadingSlots" class="loading-container small">
        <div class="loading-spinner small" />
        <p>載入可預約時段...</p>
      </div>

      <div v-else-if="slotsError" class="error-container small">
        <p>{{ slotsError }}</p>
        <button class="retry-btn" @click="loadAvailableSlots">重試</button>
      </div>

      <div v-else-if="availableSlots.length === 0" class="empty-state small">
        <p>此日期沒有可預約的時段</p>
      </div>

      <div v-else class="time-slots">
        <button
          v-for="slot in availableSlots"
          :key="slot.start_time"
          class="time-btn"
          :class="{ 'time-btn--selected': selectedTime === slot.start_time }"
          @click="selectTime(slot.start_time)"
        >
          {{ slot.start_time }}
        </button>
      </div>
    </div>

    <!-- 底部按鈕 -->
    <div class="booking-footer">
      <button
        class="next-btn"
        :disabled="!canProceed"
        @click="goToNextStep"
      >
        下一步：確認預約
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 預約流程 Step 3：選擇日期與時間
 */
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBookingApi } from '~/composables/useBookingApi'
import { useBookingStore } from '~/stores/booking'
import type { TimeSlot } from '~/composables/useBookingApi'

// 路由
const route = useRoute()
const router = useRouter()
const code = computed(() => route.params.code as string)

// API 與 Store
const bookingApi = useBookingApi()
const bookingStore = useBookingStore()

// 狀態
const selectedDate = ref('')
const selectedTime = ref('')
const loadingSlots = ref(false)
const slotsError = ref('')
const availableSlots = ref<TimeSlot[]>([])

// 主題樣式
const themeStyle = computed(() => {
  if (!bookingStore.salon?.theme_color) return {}
  return {
    '--theme-color': bookingStore.salon.theme_color,
    '--theme-color-light': `${bookingStore.salon.theme_color}15`,
    '--theme-color-dark': bookingStore.salon.theme_color
  }
})

// 生成接下來 14 天的日期選項
const dateOptions = computed(() => {
  const options = []
  const today = new Date()
  const weekdays = ['週日', '週一', '週二', '週三', '週四', '週五', '週六']
  const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']

  // 從明天開始（或今天，視預約規則而定）
  const startOffset = bookingStore.salon?.booking_rule?.min_advance_hours ?
    Math.ceil(bookingStore.salon.booking_rule.min_advance_hours / 24) : 1

  for (let i = startOffset; i <= 14; i++) {
    const date = new Date(today)
    date.setDate(today.getDate() + i)

    options.push({
      value: date.toISOString().split('T')[0],
      weekday: weekdays[date.getDay()],
      day: date.getDate().toString(),
      month: months[date.getMonth()]
    })
  }

  return options
})

// 是否可以繼續
const canProceed = computed(() => {
  return selectedDate.value && selectedTime.value
})

// 選擇日期
const selectDate = (date: string) => {
  selectedDate.value = date
  selectedTime.value = '' // 清除已選時間
  loadAvailableSlots()
}

// 選擇時間
const selectTime = (time: string) => {
  selectedTime.value = time
  bookingStore.selectDateTime(selectedDate.value, time)
}

// 載入可用時段
const loadAvailableSlots = async () => {
  if (!selectedDate.value) return
  if (!bookingStore.selectedStylist || !bookingStore.selectedService) return

  loadingSlots.value = true
  slotsError.value = ''

  try {
    const res = await bookingApi.getAvailableSlots(
      code.value,
      bookingStore.selectedStylist.id,
      bookingStore.selectedService.id,
      selectedDate.value
    )

    if (res.success && res.data) {
      availableSlots.value = res.data.slots
    } else {
      slotsError.value = '無法載入可用時段'
    }
  } catch (e) {
    console.error('Failed to load slots:', e)
    slotsError.value = '載入失敗，請稍後再試'
  } finally {
    loadingSlots.value = false
  }
}

// 返回上一步
const goBack = () => {
  router.push(`/s/${code.value}/booking/stylist`)
}

// 前往下一步
const goToNextStep = () => {
  if (canProceed.value) {
    router.push(`/s/${code.value}/booking/confirm`)
  }
}

// 初始化
onMounted(() => {
  // 檢查前置條件
  if (!bookingStore.selectedService || !bookingStore.selectedStylist) {
    router.push(`/s/${code.value}/booking`)
    return
  }

  // 恢復已選擇的日期和時間
  if (bookingStore.selectedDate) {
    selectedDate.value = bookingStore.selectedDate
    selectedTime.value = bookingStore.selectedTime
    loadAvailableSlots()
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
  padding-bottom: 100px;
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

/* 已選擇的資訊 */
.selected-info {
  padding: var(--spacing-md);
  background: var(--theme-color-light);
}

.info-row {
  display: flex;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.info-row:not(:last-child) {
  margin-bottom: var(--spacing-xs);
}

.info-label {
  color: var(--color-text-secondary);
}

.info-value {
  color: var(--color-text-primary);
  font-weight: 500;
}

/* 日期選擇 */
.date-section {
  padding: var(--spacing-lg);
}

.section-title {
  font-size: var(--font-size-md);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-md) 0;
}

.date-picker {
  display: flex;
  gap: var(--spacing-sm);
  overflow-x: auto;
  padding-bottom: var(--spacing-sm);
  -webkit-overflow-scrolling: touch;
}

.date-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  min-width: 60px;
  padding: var(--spacing-sm);
  background: var(--color-bg-card);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.date-btn:hover {
  border-color: var(--theme-color);
}

.date-btn--selected {
  border-color: var(--theme-color);
  background: var(--theme-color);
}

.date-btn--selected .date-weekday,
.date-btn--selected .date-day,
.date-btn--selected .date-month {
  color: white;
}

.date-weekday {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.date-day {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
}

.date-month {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

/* 時段選擇 */
.time-section {
  padding: 0 var(--spacing-lg) var(--spacing-lg);
}

.time-slots {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-sm);
}

.time-btn {
  padding: var(--spacing-md) var(--spacing-sm);
  background: var(--color-bg-card);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.time-btn:hover {
  border-color: var(--theme-color);
}

.time-btn--selected {
  border-color: var(--theme-color);
  background: var(--theme-color);
  color: white;
}

/* 載入與錯誤 */
.loading-container,
.error-container,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-3xl);
  text-align: center;
  color: var(--color-text-secondary);
}

.loading-container.small,
.error-container.small,
.empty-state.small {
  padding: var(--spacing-xl);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top-color: var(--theme-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--spacing-md);
}

.loading-spinner.small {
  width: 24px;
  height: 24px;
  border-width: 2px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.retry-btn {
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--theme-color);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
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

.next-btn {
  display: block;
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
}

.next-btn:disabled {
  background: var(--color-border);
  cursor: not-allowed;
}

.next-btn:not(:disabled):hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

/* 響應式 */
@media (max-width: 480px) {
  .time-slots {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
