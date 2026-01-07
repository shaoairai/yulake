<template>
  <!-- 預約成功頁面 -->
  <div class="success-page" :style="themeStyle">
    <!-- 載入中 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner" />
      <p>載入預約資訊...</p>
    </div>

    <!-- 錯誤狀態 -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">😢</div>
      <h2>無法取得預約資訊</h2>
      <p>{{ error }}</p>
      <NuxtLink :to="`/s/${code}`" class="back-link">返回店家首頁</NuxtLink>
    </div>

    <!-- 成功內容 -->
    <template v-else-if="booking">
      <!-- 成功圖示 -->
      <div class="success-header">
        <div class="success-icon">✓</div>
        <h1>預約成功！</h1>
        <p class="success-message">您的預約已送出，請準時前往</p>
      </div>

      <!-- 預約詳情卡片 -->
      <div class="booking-card">
        <div class="card-header">
          <span class="booking-id">預約編號：{{ booking.id }}</span>
          <span class="booking-status" :class="statusClass">{{ statusText }}</span>
        </div>

        <div class="card-body">
          <!-- 店家 -->
          <div class="info-row">
            <span class="info-icon">🏪</span>
            <div class="info-content">
              <span class="info-label">店家</span>
              <span class="info-value">{{ booking.salon.name }}</span>
            </div>
          </div>

          <!-- 服務 -->
          <div class="info-row">
            <span class="info-icon">✨</span>
            <div class="info-content">
              <span class="info-label">服務項目</span>
              <span class="info-value">{{ booking.service.name }}</span>
            </div>
            <span class="info-price">${{ booking.service.price }}</span>
          </div>

          <!-- 設計師 -->
          <div class="info-row">
            <span class="info-icon">💇</span>
            <div class="info-content">
              <span class="info-label">設計師</span>
              <span class="info-value">{{ booking.stylist.name }}</span>
            </div>
          </div>

          <!-- 日期時間 -->
          <div class="info-row highlight">
            <span class="info-icon">📅</span>
            <div class="info-content">
              <span class="info-label">預約時間</span>
              <span class="info-value">{{ formattedDateTime }}</span>
            </div>
          </div>

          <!-- 地點 -->
          <div class="info-row">
            <span class="info-icon">📍</span>
            <div class="info-content">
              <span class="info-label">地點</span>
              <span class="info-value">{{ booking.salon.address }}</span>
            </div>
          </div>

          <!-- 備註 -->
          <div v-if="booking.customer_note" class="info-row">
            <span class="info-icon">📝</span>
            <div class="info-content">
              <span class="info-label">備註</span>
              <span class="info-value">{{ booking.customer_note }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 提醒事項 -->
      <div class="reminder-card">
        <h3>溫馨提醒</h3>
        <ul>
          <li>請準時抵達，若需更改或取消，請提前告知</li>
          <li>若有任何問題，可撥打店家電話：{{ booking.salon.phone }}</li>
        </ul>
      </div>

      <!-- 操作按鈕 -->
      <div class="actions">
        <NuxtLink :to="`/s/${code}`" class="action-btn secondary">
          返回店家首頁
        </NuxtLink>
        <NuxtLink to="/my/bookings" class="action-btn primary">
          查看我的預約
        </NuxtLink>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
/**
 * 預約成功頁面
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useBookingApi } from '~/composables/useBookingApi'
import type { BookingInfo } from '~/composables/useBookingApi'

// 路由
const route = useRoute()
const code = computed(() => route.params.code as string)
const bookingId = computed(() => route.query.id as string)

// API
const bookingApi = useBookingApi()

// 狀態
const loading = ref(true)
const error = ref('')
const booking = ref<BookingInfo | null>(null)

// 主題樣式
const themeStyle = computed(() => {
  if (!booking.value?.salon?.theme_color) return {}
  return {
    '--theme-color': booking.value.salon.theme_color,
    '--theme-color-light': `${booking.value.salon.theme_color}15`,
    '--theme-color-dark': booking.value.salon.theme_color
  }
})

// 狀態文字
const statusText = computed(() => {
  const statusMap: Record<string, string> = {
    pending: '待確認',
    confirmed: '已確認',
    completed: '已完成',
    cancelled: '已取消',
    cancelled_by_salon: '店家取消',
    no_show: '未出席'
  }
  return statusMap[booking.value?.status || ''] || booking.value?.status
})

// 狀態樣式
const statusClass = computed(() => {
  const classMap: Record<string, string> = {
    pending: 'status--pending',
    confirmed: 'status--confirmed',
    completed: 'status--completed',
    cancelled: 'status--cancelled',
    cancelled_by_salon: 'status--cancelled',
    no_show: 'status--cancelled'
  }
  return classMap[booking.value?.status || ''] || ''
})

// 格式化日期時間
const formattedDateTime = computed(() => {
  if (!booking.value) return ''

  const date = new Date(booking.value.booking_date)
  const weekdays = ['週日', '週一', '週二', '週三', '週四', '週五', '週六']

  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  const weekday = weekdays[date.getDay()]

  return `${year}/${month}/${day} (${weekday}) ${booking.value.start_time}`
})

// 載入預約詳情
const loadBooking = async () => {
  if (!bookingId.value) {
    error.value = '無效的預約編號'
    loading.value = false
    return
  }

  try {
    const res = await bookingApi.getMyBookingDetail(bookingId.value)
    if (res.success && res.data) {
      booking.value = res.data
    } else {
      error.value = res.error || '無法載入預約資訊'
    }
  } catch (e) {
    console.error('Failed to load booking:', e)
    error.value = '載入失敗，請稍後再試'
  } finally {
    loading.value = false
  }
}

// 初始化
onMounted(() => {
  loadBooking()
})
</script>

<style scoped>
.success-page {
  --theme-color: var(--color-primary);
  --theme-color-light: var(--color-primary-light);
  --theme-color-dark: var(--color-primary-dark);

  min-height: 100vh;
  background-color: var(--color-bg);
  padding: var(--spacing-lg);
  padding-bottom: var(--spacing-3xl);
}

/* 載入與錯誤 */
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  text-align: center;
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

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-icon {
  font-size: 64px;
  margin-bottom: var(--spacing-md);
}

.error-container h2 {
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm) 0;
}

.error-container p {
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-lg) 0;
}

.back-link {
  color: var(--theme-color);
  text-decoration: none;
  font-weight: 500;
}

/* 成功標題 */
.success-header {
  text-align: center;
  padding: var(--spacing-xl) 0;
}

.success-icon {
  width: 80px;
  height: 80px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--color-success);
  color: white;
  font-size: 40px;
  font-weight: bold;
  border-radius: 50%;
  margin-bottom: var(--spacing-md);
}

.success-header h1 {
  font-size: var(--font-size-2xl);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.success-message {
  color: var(--color-text-secondary);
  margin: 0;
}

/* 預約詳情卡片 */
.booking-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  overflow: hidden;
  margin-bottom: var(--spacing-lg);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  background: var(--theme-color-light);
  border-bottom: 1px solid var(--color-border-light);
}

.booking-id {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.booking-status {
  font-size: var(--font-size-xs);
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  font-weight: 500;
}

.status--pending {
  background: var(--color-warning-light);
  color: var(--color-warning);
}

.status--confirmed {
  background: var(--color-success-light);
  color: var(--color-success);
}

.status--completed {
  background: var(--color-info-light);
  color: var(--color-info);
}

.status--cancelled {
  background: var(--color-error-light);
  color: var(--color-error);
}

.card-body {
  padding: var(--spacing-md);
}

.info-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) 0;
}

.info-row:not(:last-child) {
  border-bottom: 1px solid var(--color-border-light);
}

.info-row.highlight {
  background: var(--theme-color-light);
  margin: var(--spacing-sm) calc(var(--spacing-md) * -1);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  border-bottom: none;
}

.info-icon {
  font-size: 20px;
  width: 28px;
  text-align: center;
}

.info-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.info-value {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  font-weight: 500;
}

.info-price {
  font-size: var(--font-size-md);
  color: var(--theme-color);
  font-weight: 600;
}

/* 提醒卡片 */
.reminder-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
}

.reminder-card h3 {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm) 0;
}

.reminder-card ul {
  margin: 0;
  padding-left: var(--spacing-lg);
}

.reminder-card li {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.6;
}

/* 操作按鈕 */
.actions {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.action-btn {
  flex: 1;
  min-width: 140px;
  padding: var(--spacing-md);
  border-radius: var(--radius-lg);
  font-size: var(--font-size-sm);
  font-weight: 600;
  text-align: center;
  text-decoration: none;
  transition: all var(--transition-fast);
}

.action-btn.primary {
  background: var(--theme-color);
  color: white;
}

.action-btn.primary:hover {
  opacity: 0.9;
}

.action-btn.secondary {
  background: var(--color-bg-card);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.action-btn.secondary:hover {
  border-color: var(--theme-color);
}
</style>
