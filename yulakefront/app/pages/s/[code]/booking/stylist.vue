<template>
  <!-- 選擇設計師頁面 -->
  <div class="booking-page" :style="themeStyle">
    <!-- 進度指示器 -->
    <div class="booking-progress">
      <div class="progress-step completed">
        <span class="step-number">✓</span>
        <span class="step-label">選擇服務</span>
      </div>
      <div class="progress-line completed" />
      <div class="progress-step active">
        <span class="step-number">2</span>
        <span class="step-label">選擇設計師</span>
      </div>
      <div class="progress-line" />
      <div class="progress-step">
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
        <span>返回選擇服務</span>
      </button>
    </header>

    <!-- 已選擇的服務 -->
    <div v-if="bookingStore.selectedService" class="selected-service">
      <span class="selected-label">已選擇：</span>
      <span class="selected-name">{{ bookingStore.selectedService.name }}</span>
      <span class="selected-price">${{ bookingStore.selectedService.price }}</span>
    </div>

    <!-- 載入中 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner" />
      <p>載入設計師資料...</p>
    </div>

    <!-- 錯誤狀態 -->
    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="loadStylists">重試</button>
    </div>

    <!-- 設計師列表 -->
    <div v-else class="stylists-container">
      <h2 class="section-title">選擇設計師</h2>

      <div v-if="stylists.length === 0" class="empty-state">
        <p>目前沒有可選擇的設計師</p>
      </div>

      <div v-else class="stylists-list">
        <div
          v-for="stylist in stylists"
          :key="stylist.id"
          class="stylist-card"
          :class="{ 'stylist-card--selected': selectedStylistId === stylist.id }"
          @click="selectStylist(stylist)"
        >
          <div class="stylist-avatar">
            <img v-if="stylist.avatar_url" :src="stylist.avatar_url" :alt="stylist.name">
            <span v-else class="avatar-placeholder">{{ stylist.name.charAt(0) }}</span>
          </div>
          <div class="stylist-info">
            <h3 class="stylist-name">{{ stylist.name }}</h3>
            <p v-if="stylist.style" class="stylist-style">{{ stylist.style }}</p>
            <p v-if="stylist.introduction" class="stylist-intro">{{ stylist.introduction }}</p>
          </div>
          <div class="stylist-check">
            <span v-if="selectedStylistId === stylist.id" class="check-icon">✓</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部按鈕 -->
    <div class="booking-footer">
      <button
        class="next-btn"
        :disabled="!selectedStylistId"
        @click="goToNextStep"
      >
        下一步：選擇時間
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 預約流程 Step 2：選擇設計師
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBookingApi } from '~/composables/useBookingApi'
import { useBookingStore } from '~/stores/booking'
import type { StylistInfo } from '~/composables/useBookingApi'

// 路由
const route = useRoute()
const router = useRouter()
const code = computed(() => route.params.code as string)

// API 與 Store
const bookingApi = useBookingApi()
const bookingStore = useBookingStore()

// 狀態
const loading = ref(true)
const error = ref('')
const stylists = ref<StylistInfo[]>([])
const selectedStylistId = ref<string | null>(null)

// 主題樣式
const themeStyle = computed(() => {
  if (!bookingStore.salon?.theme_color) return {}
  return {
    '--theme-color': bookingStore.salon.theme_color,
    '--theme-color-light': `${bookingStore.salon.theme_color}15`,
    '--theme-color-dark': bookingStore.salon.theme_color
  }
})

// 選擇設計師
const selectStylist = (stylist: StylistInfo) => {
  selectedStylistId.value = stylist.id
  bookingStore.selectStylist(stylist)
}

// 載入設計師列表
const loadStylists = async () => {
  loading.value = true
  error.value = ''

  try {
    // 確認已選擇服務
    if (!bookingStore.selectedService) {
      router.push(`/s/${code.value}/booking`)
      return
    }

    // 載入設計師列表（可選擇性地根據服務篩選）
    const res = await bookingApi.getStylists(code.value, bookingStore.selectedService.id)
    if (res.success && res.data) {
      stylists.value = res.data
    } else {
      error.value = '無法載入設計師列表'
    }
  } catch (e) {
    console.error('Failed to load stylists:', e)
    error.value = '載入失敗，請稍後再試'
  } finally {
    loading.value = false
  }
}

// 返回上一步
const goBack = () => {
  router.push(`/s/${code.value}/booking`)
}

// 前往下一步
const goToNextStep = () => {
  if (selectedStylistId.value) {
    router.push(`/s/${code.value}/booking/time`)
  }
}

// 初始化
onMounted(() => {
  // 如果沒有選擇服務，返回服務選擇頁
  if (!bookingStore.selectedService) {
    router.push(`/s/${code.value}/booking`)
    return
  }

  // 如果已經有選擇的設計師，恢復選擇
  if (bookingStore.selectedStylist) {
    selectedStylistId.value = bookingStore.selectedStylist.id
  }

  loadStylists()
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

/* 已選擇的服務 */
.selected-service {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: var(--theme-color-light);
  font-size: var(--font-size-sm);
}

.selected-label {
  color: var(--color-text-secondary);
}

.selected-name {
  flex: 1;
  color: var(--color-text-primary);
  font-weight: 500;
}

.selected-price {
  color: var(--theme-color);
  font-weight: 600;
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

.retry-btn {
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--theme-color);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
}

/* 設計師列表 */
.stylists-container {
  padding: var(--spacing-lg);
}

.section-title {
  font-size: var(--font-size-lg);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-lg) 0;
}

.stylists-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.stylist-card {
  display: flex;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: var(--color-bg-card);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.stylist-card:hover {
  border-color: var(--theme-color);
}

.stylist-card--selected {
  border-color: var(--theme-color);
  background: var(--theme-color-light);
}

.stylist-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  background: var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
}

.stylist-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 24px;
  font-weight: 600;
  color: var(--theme-color);
}

.stylist-info {
  flex: 1;
  min-width: 0;
}

.stylist-name {
  font-size: var(--font-size-md);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.stylist-style {
  font-size: var(--font-size-sm);
  color: var(--theme-color);
  margin: 0 0 var(--spacing-xs) 0;
}

.stylist-intro {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.stylist-check {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  flex-shrink: 0;
}

.check-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--theme-color);
  color: white;
  border-radius: 50%;
  font-size: 14px;
  font-weight: bold;
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
</style>
