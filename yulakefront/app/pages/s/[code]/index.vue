<template>
  <!-- 店家公開首頁 -->
  <div class="salon-page" :style="themeStyle">
    <!-- 載入中 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner" />
      <p>載入中...</p>
    </div>

    <!-- 錯誤狀態 -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">😢</div>
      <h2>找不到店家</h2>
      <p>{{ error }}</p>
      <NuxtLink to="/" class="back-link">返回首頁</NuxtLink>
    </div>

    <!-- 店家內容 -->
    <template v-else-if="salon">
      <!-- Header -->
      <header class="salon-header">
        <div class="salon-logo">
          <img v-if="salon.logo_url" :src="salon.logo_url" :alt="salon.name">
          <span v-else class="logo-placeholder">{{ salon.name.charAt(0) }}</span>
        </div>
        <h1 class="salon-name">{{ salon.name }}</h1>
      </header>

      <!-- 店家資訊 -->
      <section class="salon-info">
        <div v-if="salon.address" class="info-item">
          <span class="info-icon">📍</span>
          <span class="info-text">{{ salon.address }}</span>
        </div>
        <div v-if="salon.phone" class="info-item">
          <span class="info-icon">📞</span>
          <a :href="`tel:${salon.phone}`" class="info-text info-link">{{ salon.phone }}</a>
        </div>
        <div v-if="salon.line_id" class="info-item">
          <span class="info-icon">💬</span>
          <span class="info-text">LINE: {{ salon.line_id }}</span>
        </div>
        <div v-if="salon.ig_account" class="info-item">
          <span class="info-icon">📷</span>
          <a :href="`https://instagram.com/${salon.ig_account}`" target="_blank" class="info-text info-link">
            @{{ salon.ig_account }}
          </a>
        </div>
      </section>

      <!-- 營業時間 -->
      <section class="business-hours">
        <h2 class="section-title">營業時間</h2>
        <div class="hours-list">
          <div
            v-for="hour in sortedBusinessHours"
            :key="hour.day_of_week"
            class="hour-item"
            :class="{ 'hour-item--closed': !hour.is_open, 'hour-item--today': isToday(hour.day_of_week) }"
          >
            <span class="day-name">{{ getDayName(hour.day_of_week) }}</span>
            <span v-if="hour.is_open" class="hour-time">
              {{ hour.open_time }} - {{ hour.close_time }}
            </span>
            <span v-else class="hour-closed">公休</span>
          </div>
        </div>
      </section>

      <!-- 底部行動按鈕 -->
      <div class="booking-cta">
        <div class="cta-container">
          <NuxtLink :to="`/s/${code}/booking`" class="booking-button">
            開始預約
          </NuxtLink>
          <NuxtLink
            v-if="!isAuthenticated"
            to="/auth/login"
            class="login-button"
            @click="saveRedirect"
          >
            登入 / 註冊
          </NuxtLink>
          <NuxtLink v-else to="/my/bookings" class="login-button">
            我的預約
          </NuxtLink>
        </div>
      </div>

      <!-- 底部 -->
      <footer class="salon-footer">
        <p>Powered by <NuxtLink to="/">約來客 Yulake</NuxtLink></p>
      </footer>
    </template>
  </div>
</template>

<script setup lang="ts">
/**
 * 店家公開首頁
 * 顯示店家資訊與預約入口
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useBookingApi } from '~/composables/useBookingApi'
import { useBookingStore } from '~/stores/booking'
import { useAuth } from '~/composables/useAuth'
import type { SalonPublicInfo } from '~/composables/useBookingApi'

// 路由參數
const route = useRoute()
const code = computed(() => route.params.code as string)

// API 與狀態
const bookingApi = useBookingApi()
const bookingStore = useBookingStore()
const { isAuthenticated } = useAuth()

// 登入前儲存當前路徑
const saveRedirect = () => {
  sessionStorage.setItem('redirectAfterLogin', route.fullPath)
}

// 本地狀態
const loading = ref(true)
const error = ref('')
const salon = ref<SalonPublicInfo | null>(null)

// 主題樣式
const themeStyle = computed(() => {
  if (!salon.value?.theme_color) return {}
  return {
    '--theme-color': salon.value.theme_color,
    '--theme-color-light': `${salon.value.theme_color}15`,
    '--theme-color-dark': salon.value.theme_color
  }
})

// 排序後的營業時間（從週日開始）
const sortedBusinessHours = computed(() => {
  if (!salon.value?.business_hours) return []
  return [...salon.value.business_hours].sort((a, b) => a.day_of_week - b.day_of_week)
})

// 取得星期名稱
const getDayName = (day: number): string => {
  const days = ['週日', '週一', '週二', '週三', '週四', '週五', '週六']
  return days[day] || ''
}

// 判斷是否為今天
const isToday = (day: number): boolean => {
  const today = new Date().getDay()
  return today === day
}

// 載入店家資料
const loadSalon = async () => {
  loading.value = true
  error.value = ''

  try {
    const res = await bookingApi.getSalonInfo(code.value)
    if (res.success && res.data) {
      salon.value = res.data
      // 儲存到 store
      bookingStore.setSalon(res.data)
    } else {
      error.value = '此店家不存在或已停用'
    }
  } catch (e) {
    console.error('Failed to load salon:', e)
    error.value = '載入失敗，請稍後再試'
  } finally {
    loading.value = false
  }
}

// 初始化
onMounted(() => {
  loadSalon()
})
</script>

<style scoped>
.salon-page {
  --theme-color: var(--color-primary);
  --theme-color-light: var(--color-primary-light);
  --theme-color-dark: var(--color-primary-dark);

  min-height: 100vh;
  background-color: var(--color-bg);
  padding-bottom: 100px;
}

/* 載入與錯誤狀態 */
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  text-align: center;
  padding: var(--spacing-xl);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top-color: var(--theme-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
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
  margin-bottom: var(--spacing-sm);
}

.error-container p {
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-lg);
}

.back-link {
  color: var(--theme-color);
  text-decoration: none;
  font-weight: 500;
}

/* Header */
.salon-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-2xl) var(--spacing-lg);
  background: linear-gradient(135deg, var(--theme-color-light) 0%, var(--color-bg) 100%);
}

.salon-logo {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  background: white;
  box-shadow: var(--shadow-lg);
  margin-bottom: var(--spacing-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.salon-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.logo-placeholder {
  font-size: 48px;
  font-weight: 700;
  color: var(--theme-color);
}

.salon-name {
  font-size: var(--font-size-2xl);
  color: var(--color-text-primary);
  margin: 0;
  text-align: center;
}

/* 店家資訊 */
.salon-info {
  padding: var(--spacing-lg);
  background: var(--color-bg-card);
  margin: var(--spacing-md);
  border-radius: var(--radius-lg);
}

.info-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) 0;
}

.info-item:not(:last-child) {
  border-bottom: 1px solid var(--color-border-light);
}

.info-icon {
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.info-text {
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
}

.info-link {
  color: var(--theme-color);
  text-decoration: none;
}

/* 營業時間 */
.business-hours {
  padding: var(--spacing-lg);
  margin: var(--spacing-md);
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
}

.section-title {
  font-size: var(--font-size-md);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-md) 0;
}

.hours-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.hour-item {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-sm);
  border-radius: var(--radius-sm);
}

.hour-item--today {
  background-color: var(--theme-color-light);
}

.hour-item--closed .day-name,
.hour-item--closed .hour-closed {
  color: var(--color-text-muted);
}

.day-name {
  font-weight: 500;
  color: var(--color-text-primary);
}

.hour-time {
  color: var(--color-text-secondary);
}

.hour-closed {
  color: var(--color-text-muted);
}

/* 底部行動按鈕 */
.booking-cta {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: var(--spacing-md);
  background: var(--color-bg-card);
  border-top: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-lg);
}

.cta-container {
  display: flex;
  gap: var(--spacing-sm);
  max-width: 400px;
  margin: 0 auto;
}

.booking-button {
  flex: 1;
  display: block;
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--theme-color);
  color: white;
  text-align: center;
  text-decoration: none;
  font-size: var(--font-size-md);
  font-weight: 600;
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
}

.booking-button:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.login-button {
  display: block;
  padding: var(--spacing-md) var(--spacing-lg);
  background: transparent;
  color: var(--theme-color);
  text-align: center;
  text-decoration: none;
  font-size: var(--font-size-md);
  font-weight: 500;
  border: 1px solid var(--theme-color);
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.login-button:hover {
  background: var(--theme-color-light);
}

/* Footer */
.salon-footer {
  text-align: center;
  padding: var(--spacing-xl);
  color: var(--color-text-muted);
  font-size: var(--font-size-xs);
}

.salon-footer a {
  color: var(--theme-color);
  text-decoration: none;
}
</style>
