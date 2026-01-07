<template>
  <!-- 選擇服務頁面 -->
  <div class="booking-page" :style="themeStyle">
    <!-- 進度指示器 -->
    <div class="booking-progress">
      <div class="progress-step active">
        <span class="step-number">1</span>
        <span class="step-label">選擇服務</span>
      </div>
      <div class="progress-line" />
      <div class="progress-step">
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

    <!-- 店家資訊 -->
    <header class="salon-header">
      <NuxtLink :to="`/s/${code}`" class="back-link">
        <span class="back-icon">←</span>
        <span v-if="bookingStore.salon">{{ bookingStore.salon.name }}</span>
      </NuxtLink>
    </header>

    <!-- 載入中 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner" />
      <p>載入服務項目...</p>
    </div>

    <!-- 錯誤狀態 -->
    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="loadServices">重試</button>
    </div>

    <!-- 服務列表 -->
    <div v-else class="services-container">
      <h2 class="section-title">選擇服務項目</h2>

      <div v-if="services.length === 0" class="empty-state">
        <p>目前沒有可預約的服務</p>
      </div>

      <div v-else class="services-list">
        <div
          v-for="service in services"
          :key="service.id"
          class="service-card"
          :class="{ 'service-card--selected': selectedServiceId === service.id }"
          @click="selectService(service)"
        >
          <div v-if="service.image_url" class="service-image">
            <img :src="service.image_url" :alt="service.name">
          </div>
          <div class="service-info">
            <h3 class="service-name">{{ service.name }}</h3>
            <p v-if="service.description" class="service-desc">{{ service.description }}</p>
            <div class="service-meta">
              <span class="service-duration">⏱️ {{ service.duration }} 分鐘</span>
              <span class="service-price">${{ service.price }}</span>
            </div>
          </div>
          <div class="service-check">
            <span v-if="selectedServiceId === service.id" class="check-icon">✓</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部按鈕 -->
    <div class="booking-footer">
      <button
        class="next-btn"
        :disabled="!selectedServiceId"
        @click="goToNextStep"
      >
        下一步：選擇設計師
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 預約流程 Step 1：選擇服務
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBookingApi } from '~/composables/useBookingApi'
import { useBookingStore } from '~/stores/booking'
import type { ServiceItem } from '~/composables/useBookingApi'

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
const services = ref<ServiceItem[]>([])
const selectedServiceId = ref<string | null>(null)

// 主題樣式
const themeStyle = computed(() => {
  if (!bookingStore.salon?.theme_color) return {}
  return {
    '--theme-color': bookingStore.salon.theme_color,
    '--theme-color-light': `${bookingStore.salon.theme_color}15`,
    '--theme-color-dark': bookingStore.salon.theme_color
  }
})

// 選擇服務
const selectService = (service: ServiceItem) => {
  selectedServiceId.value = service.id
  bookingStore.selectService(service)
}

// 載入服務列表
const loadServices = async () => {
  loading.value = true
  error.value = ''

  try {
    // 如果 store 沒有店家資訊，先載入
    if (!bookingStore.salon) {
      const salonRes = await bookingApi.getSalonInfo(code.value)
      if (salonRes.success && salonRes.data) {
        bookingStore.setSalon(salonRes.data)
      } else {
        error.value = '無法載入店家資訊'
        loading.value = false
        return
      }
    }

    // 載入服務列表
    const res = await bookingApi.getServices(code.value)
    if (res.success && res.data) {
      services.value = res.data
    } else {
      error.value = '無法載入服務列表'
    }
  } catch (e) {
    console.error('Failed to load services:', e)
    error.value = '載入失敗，請稍後再試'
  } finally {
    loading.value = false
  }
}

// 前往下一步
const goToNextStep = () => {
  if (selectedServiceId.value) {
    router.push(`/s/${code.value}/booking/stylist`)
  }
}

// 初始化
onMounted(() => {
  // 如果已經有選擇的服務，恢復選擇
  if (bookingStore.selectedService) {
    selectedServiceId.value = bookingStore.selectedService.id
  }
  loadServices()
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

/* Header */
.salon-header {
  padding: var(--spacing-md);
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border-light);
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  color: var(--theme-color);
  text-decoration: none;
  font-weight: 500;
}

.back-icon {
  font-size: 18px;
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

/* 服務列表 */
.services-container {
  padding: var(--spacing-lg);
}

.section-title {
  font-size: var(--font-size-lg);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-lg) 0;
}

.services-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.service-card {
  display: flex;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: var(--color-bg-card);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.service-card:hover {
  border-color: var(--theme-color);
}

.service-card--selected {
  border-color: var(--theme-color);
  background: var(--theme-color-light);
}

.service-image {
  width: 80px;
  height: 80px;
  border-radius: var(--radius-md);
  overflow: hidden;
  flex-shrink: 0;
}

.service-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.service-info {
  flex: 1;
  min-width: 0;
}

.service-name {
  font-size: var(--font-size-md);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.service-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-sm) 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.service-meta {
  display: flex;
  gap: var(--spacing-md);
  font-size: var(--font-size-sm);
}

.service-duration {
  color: var(--color-text-secondary);
}

.service-price {
  color: var(--theme-color);
  font-weight: 600;
}

.service-check {
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
