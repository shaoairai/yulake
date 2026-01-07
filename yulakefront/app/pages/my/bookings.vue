<template>
  <!-- 顧客前台 - 我的預約 -->
  <div class="my-bookings-page">
    <!-- 頁面標題 -->
    <div class="page-header">
      <h1 class="page-title">我的預約</h1>
      <p class="page-description">查看並管理您的預約紀錄</p>
    </div>

    <!-- 視圖切換 -->
    <div class="view-tabs">
      <button
        :class="['view-tab', { active: currentView === 'calendar' }]"
        @click="currentView = 'calendar'"
      >
        日曆視圖
      </button>
      <button
        :class="['view-tab', { active: currentView === 'list' }]"
        @click="currentView = 'list'"
      >
        列表視圖
      </button>
    </div>

    <!-- 日曆視圖 -->
    <div v-if="currentView === 'calendar'" class="calendar-section">
      <AppCalendar
        :events="myBookings"
        initial-view="month"
        @event-click="handleEventClick"
        @date-click="handleDateClick"
      />
    </div>

    <!-- 列表視圖 -->
    <div v-else class="list-section">
      <!-- 篩選 -->
      <div class="list-filters">
        <AppSelect
          v-model="listFilter"
          :options="filterOptions"
          placeholder="全部預約"
        />
      </div>

      <!-- 預約列表 -->
      <div v-if="filteredBookings.length > 0" class="booking-list">
        <div
          v-for="booking in filteredBookings"
          :key="booking.id"
          class="booking-card"
          @click="handleEventClick(booking)"
        >
          <div class="booking-card__header">
            <span class="booking-card__date">{{ formatDate(booking.date) }}</span>
            <AppBadge :variant="getStatusVariant(booking.status)" size="sm">
              {{ getStatusLabel(booking.status) }}
            </AppBadge>
          </div>
          <div class="booking-card__body">
            <div class="booking-card__service">{{ booking.serviceName }}</div>
            <div class="booking-card__details">
              <span class="booking-card__time">{{ booking.startTime }} - {{ booking.endTime }}</span>
              <span class="booking-card__stylist">{{ booking.stylistName }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 空狀態 -->
      <div v-else class="empty-state">
        <span class="empty-icon">📅</span>
        <p class="empty-title">目前沒有預約</p>
        <p class="empty-description">前往店家預約頁面開始預約吧！</p>
      </div>
    </div>

    <!-- 預約詳情 Modal -->
    <AppModal
      v-model="showDetailModal"
      :title="selectedBooking ? '預約詳情' : ''"
    >
      <div v-if="selectedBooking" class="booking-detail">
        <div class="detail-row">
          <span class="detail-label">店家</span>
          <span class="detail-value">{{ selectedBooking.salon.name }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">服務項目</span>
          <span class="detail-value">{{ selectedBooking.service.name }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">設計師</span>
          <span class="detail-value">{{ selectedBooking.stylist.name }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">日期</span>
          <span class="detail-value">{{ formatFullDate(selectedBooking.booking_date) }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">時間</span>
          <span class="detail-value">{{ selectedBooking.start_time }} - {{ selectedBooking.end_time }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">狀態</span>
          <span class="detail-value">
            <AppBadge :variant="getStatusVariant(selectedBooking.status)">
              {{ getStatusLabel(selectedBooking.status) }}
            </AppBadge>
          </span>
        </div>
        <div v-if="selectedBooking.customer_note" class="detail-row">
          <span class="detail-label">備註</span>
          <span class="detail-value detail-note">{{ selectedBooking.customer_note }}</span>
        </div>

        <!-- 取消預約按鈕 -->
        <div
          v-if="canCancelBooking({ status: selectedBooking.status, date: selectedBooking.booking_date, startTime: selectedBooking.start_time })"
          class="detail-actions"
        >
          <AppButton
            variant="danger"
            size="sm"
            @click="cancelBooking"
          >
            取消預約
          </AppButton>
        </div>
      </div>

      <template #footer>
        <AppButton variant="ghost" @click="showDetailModal = false">
          關閉
        </AppButton>
      </template>
    </AppModal>
  </div>
</template>

<script setup lang="ts">
/**
 * 顧客前台 - 我的預約頁面
 * 顯示顧客自己的所有預約（日曆/列表視圖）
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBookingApi } from '~/composables/useBookingApi'
import { useAuth } from '~/composables/useAuth'
import type { BookingInfo } from '~/composables/useBookingApi'

// 預約狀態類型
type BookingStatus = 'pending' | 'confirmed' | 'completed' | 'cancelled' | 'cancelled_by_salon' | 'no_show'

// 設定使用 default layout
definePageMeta({
  layout: 'default'
})

const router = useRouter()
const bookingApi = useBookingApi()
const { isAuthenticated, checkAuth } = useAuth()

// 狀態
const loading = ref(true)
const bookings = ref<BookingInfo[]>([])
const currentView = ref<'calendar' | 'list'>('list')
const listFilter = ref('')
const showDetailModal = ref(false)
const selectedBooking = ref<BookingInfo | null>(null)

// 篩選選項
const filterOptions = [
  { value: '', label: '全部預約' },
  { value: 'upcoming', label: '即將到來' },
  { value: 'past', label: '已結束' },
  { value: 'cancelled', label: '已取消' }
]

// 狀態標籤
const statusLabels: Record<string, string> = {
  pending: '待確認',
  confirmed: '已確認',
  completed: '已完成',
  cancelled: '已取消',
  cancelled_by_salon: '店家取消',
  no_show: '未出席'
}

// 狀態樣式
const statusVariants: Record<string, 'default' | 'primary' | 'success' | 'warning' | 'error'> = {
  pending: 'warning',
  confirmed: 'success',
  completed: 'primary',
  cancelled: 'default',
  cancelled_by_salon: 'error',
  no_show: 'error'
}

// 載入預約列表
const loadBookings = async () => {
  loading.value = true
  try {
    const res = await bookingApi.getMyBookings()
    if (res.success && res.data) {
      bookings.value = res.data
    }
  } catch (e) {
    console.error('Failed to load bookings:', e)
  } finally {
    loading.value = false
  }
}

// 我的預約（轉換為日曆格式）
const myBookings = computed(() => {
  return bookings.value.map(b => ({
    id: b.id,
    date: b.booking_date,
    startTime: b.start_time,
    endTime: b.end_time,
    serviceName: b.service.name,
    stylistName: b.stylist.name,
    status: b.status as BookingStatus,
    note: b.customer_note,
    // 原始資料
    _raw: b
  }))
})

// 列表篩選後的預約
const filteredBookings = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  return myBookings.value.filter(booking => {
    const bookingDate = new Date(booking.date)
    bookingDate.setHours(0, 0, 0, 0)

    if (listFilter.value === 'upcoming') {
      return bookingDate >= today &&
        (booking.status === 'pending' || booking.status === 'confirmed')
    }
    if (listFilter.value === 'past') {
      return bookingDate < today ||
        booking.status === 'completed' ||
        booking.status === 'no_show'
    }
    if (listFilter.value === 'cancelled') {
      return booking.status === 'cancelled' ||
        booking.status === 'cancelled_by_salon'
    }
    return true
  }).sort((a, b) => {
    // 依日期排序，最新的在前面
    return new Date(b.date).getTime() - new Date(a.date).getTime()
  })
})

// 工具函式
const getStatusLabel = (status: string): string => {
  return statusLabels[status] || status
}

const getStatusVariant = (status: string) => {
  return statusVariants[status] || 'default'
}

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  const month = date.getMonth() + 1
  const day = date.getDate()
  const weekDays = ['日', '一', '二', '三', '四', '五', '六']
  const weekDay = weekDays[date.getDay()]
  return `${month}/${day}（${weekDay}）`
}

const formatFullDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  const weekDays = ['日', '一', '二', '三', '四', '五', '六']
  const weekDay = weekDays[date.getDay()]
  return `${year}年${month}月${day}日（${weekDay}）`
}

const canCancelBooking = (booking: { status: string; date: string; startTime: string }): boolean => {
  // 只有待確認和已確認的預約可以取消
  if (booking.status !== 'pending' && booking.status !== 'confirmed') {
    return false
  }
  // 檢查是否在可取消時間內（假設需要提前 24 小時）
  const bookingDateTime = new Date(`${booking.date}T${booking.startTime}`)
  const now = new Date()
  const hoursUntilBooking = (bookingDateTime.getTime() - now.getTime()) / (1000 * 60 * 60)
  return hoursUntilBooking > 24
}

// 事件處理
const handleEventClick = (event: typeof myBookings.value[0]) => {
  selectedBooking.value = event._raw
  showDetailModal.value = true
}

const handleDateClick = (dateStr: string) => {
  console.log('Date clicked:', dateStr)
}

const cancelBooking = async () => {
  if (selectedBooking.value && confirm('確定要取消此預約嗎？')) {
    try {
      const res = await bookingApi.cancelMyBooking(selectedBooking.value.id, '顧客自行取消')
      if (res.success) {
        // 重新載入列表
        await loadBookings()
        showDetailModal.value = false
      }
    } catch (e) {
      console.error('Failed to cancel booking:', e)
      alert('取消失敗，請稍後再試')
    }
  }
}

// 初始化
onMounted(async () => {
  // 檢查登入狀態
  await checkAuth()
  if (!isAuthenticated.value) {
    sessionStorage.setItem('redirectAfterLogin', '/my/bookings')
    router.push('/auth/login')
    return
  }
  loadBookings()
})
</script>

<style scoped>
.my-bookings-page {
  max-width: 900px;
  margin: 0 auto;
}

/* 頁面標題 */
.page-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.page-title {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.page-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

/* 視圖切換 */
.view-tabs {
  display: flex;
  justify-content: center;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-lg);
  background-color: var(--color-bg);
  padding: 4px;
  border-radius: var(--radius-lg);
  width: fit-content;
  margin-left: auto;
  margin-right: auto;
}

.view-tab {
  padding: var(--spacing-sm) var(--spacing-lg);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.view-tab:hover {
  color: var(--color-text-primary);
}

.view-tab.active {
  background-color: var(--color-bg-card);
  color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

/* 日曆區塊 */
.calendar-section {
  background-color: var(--color-bg-card);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

/* 列表視圖 */
.list-section {
  background-color: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}

.list-filters {
  margin-bottom: var(--spacing-lg);
  max-width: 200px;
}

/* 預約卡片 */
.booking-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.booking-card {
  padding: var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.booking-card:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.booking-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.booking-card__date {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-primary);
}

.booking-card__body {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.booking-card__service {
  font-size: var(--font-size-base);
  font-weight: 500;
  color: var(--color-text-primary);
}

.booking-card__details {
  display: flex;
  gap: var(--spacing-md);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* 空狀態 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-2xl);
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: var(--spacing-md);
  opacity: 0.5;
}

.empty-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-sm) 0;
}

.empty-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin: 0;
}

/* 預約詳情 */
.booking-detail {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.detail-row {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
}

.detail-label {
  flex-shrink: 0;
  width: 80px;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.detail-value {
  flex: 1;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.detail-note {
  white-space: pre-wrap;
  background-color: var(--color-bg);
  padding: var(--spacing-sm);
  border-radius: var(--radius-md);
}

.detail-actions {
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-light);
}

/* 響應式 */
@media (max-width: 768px) {
  .page-title {
    font-size: var(--font-size-xl);
  }

  .view-tabs {
    width: 100%;
  }

  .view-tab {
    flex: 1;
  }

  .list-filters {
    max-width: none;
  }
}
</style>
