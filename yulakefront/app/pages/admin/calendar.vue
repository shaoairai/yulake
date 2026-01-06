<template>
  <!-- 廠商後台 - 日曆視圖 -->
  <div class="admin-calendar-page">
    <!-- 頁面標題 -->
    <AdminPageHeader
      title="預約日曆"
      description="以日曆視圖管理所有預約，一目了然掌握排程"
    >
      <template #actions>
        <AppButton variant="outline" size="sm" @click="goToBookings">
          列表視圖
        </AppButton>
        <AppButton variant="primary" size="sm" @click="handleAddBooking">
          ＋ 新增預約
        </AppButton>
      </template>
    </AdminPageHeader>

    <!-- 篩選列 -->
    <div class="calendar-filters">
      <div class="filter-group">
        <label>設計師</label>
        <AppSelect
          v-model="selectedStylist"
          :options="stylistOptions"
          placeholder="全部設計師"
        />
      </div>
      <div class="filter-group">
        <label>狀態</label>
        <AppSelect
          v-model="selectedStatus"
          :options="statusOptions"
          placeholder="全部狀態"
        />
      </div>
    </div>

    <!-- 日曆元件 -->
    <div class="calendar-wrapper">
      <AppCalendar
        :events="filteredBookings"
        initial-view="week"
        @event-click="handleEventClick"
        @date-click="handleDateClick"
        @view-change="handleViewChange"
      />
    </div>

    <!-- 預約詳情 Modal -->
    <AppModal
      v-model="showBookingModal"
      :title="selectedBooking ? `預約詳情 - ${selectedBooking.customerName}` : '預約詳情'"
    >
      <div v-if="selectedBooking" class="booking-detail">
        <div class="booking-detail__row">
          <span class="booking-detail__label">顧客</span>
          <span class="booking-detail__value">{{ selectedBooking.customerName }}</span>
        </div>
        <div class="booking-detail__row">
          <span class="booking-detail__label">電話</span>
          <span class="booking-detail__value">{{ selectedBooking.customerPhone }}</span>
        </div>
        <div class="booking-detail__row">
          <span class="booking-detail__label">服務</span>
          <span class="booking-detail__value">{{ selectedBooking.serviceName }}</span>
        </div>
        <div class="booking-detail__row">
          <span class="booking-detail__label">設計師</span>
          <span class="booking-detail__value">{{ selectedBooking.stylistName }}</span>
        </div>
        <div class="booking-detail__row">
          <span class="booking-detail__label">日期</span>
          <span class="booking-detail__value">{{ formatDate(selectedBooking.date) }}</span>
        </div>
        <div class="booking-detail__row">
          <span class="booking-detail__label">時間</span>
          <span class="booking-detail__value">{{ selectedBooking.startTime }} - {{ selectedBooking.endTime }}</span>
        </div>
        <div class="booking-detail__row">
          <span class="booking-detail__label">狀態</span>
          <span class="booking-detail__value">
            <AppBadge :variant="getStatusVariant(selectedBooking.status)">
              {{ getStatusLabel(selectedBooking.status) }}
            </AppBadge>
          </span>
        </div>
        <div v-if="selectedBooking.note" class="booking-detail__row">
          <span class="booking-detail__label">備註</span>
          <span class="booking-detail__value booking-detail__note">{{ selectedBooking.note }}</span>
        </div>

        <!-- 狀態操作按鈕 -->
        <div v-if="canChangeStatus(selectedBooking.status)" class="booking-detail__actions">
          <AppButton
            v-if="selectedBooking.status === 'pending'"
            variant="primary"
            size="sm"
            @click="confirmBooking"
          >
            確認預約
          </AppButton>
          <AppButton
            v-if="selectedBooking.status === 'confirmed'"
            variant="primary"
            size="sm"
            @click="completeBooking"
          >
            標記完成
          </AppButton>
          <AppButton
            v-if="selectedBooking.status === 'confirmed'"
            variant="danger"
            size="sm"
            @click="markNoShow"
          >
            標記未出席
          </AppButton>
          <AppButton
            v-if="selectedBooking.status === 'pending' || selectedBooking.status === 'confirmed'"
            variant="outline"
            size="sm"
            @click="cancelBooking"
          >
            取消預約
          </AppButton>
        </div>
      </div>

      <template #footer>
        <AppButton variant="ghost" @click="showBookingModal = false">
          關閉
        </AppButton>
      </template>
    </AppModal>
  </div>
</template>

<script setup lang="ts">
/**
 * 廠商後台 - 日曆視圖頁面
 * 以日曆形式顯示所有預約
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminApi } from '~/composables/useAdminApi'
import type { BookingStatus, AdminBooking, AdminStylist } from '~/composables/useAdminApi'

// 設定使用 admin layout 與認證
definePageMeta({
  layout: 'admin',
  middleware: 'auth'
})

// 路由
const router = useRouter()

// API
const adminApi = useAdminApi()

// 本地狀態
const loading = ref(false)

// 本地預約介面（保持 template 相容）
interface LocalBooking {
  id: string
  date: string
  startTime: string
  endTime: string
  customerName: string
  customerPhone: string
  serviceName: string
  stylistId: string
  stylistName: string
  status: BookingStatus
  note?: string
}

const bookings = ref<LocalBooking[]>([])

// 本地設計師介面
interface LocalStylist {
  id: string
  name: string
  isActive: boolean
}

const stylists = ref<LocalStylist[]>([])

// 載入預約資料（日曆使用 getCalendarData）
const loadCalendarData = async () => {
  loading.value = true
  try {
    // 預設取得今天起 30 天的預約
    const today = new Date()
    const endDate = new Date()
    endDate.setDate(endDate.getDate() + 30)

    const startStr = today.toISOString().split('T')[0]
    const endStr = endDate.toISOString().split('T')[0]

    const res = await adminApi.getCalendarData(startStr, endStr)
    if (res.success && res.data) {
      bookings.value = res.data.map((b: AdminBooking) => ({
        id: b.id,
        date: b.booking_date,
        startTime: b.start_time,
        endTime: b.end_time,
        customerName: b.customer?.name || '顧客',
        customerPhone: b.customer?.phone || '',
        serviceName: b.service?.name || '服務',
        stylistId: b.stylist?.id || '',
        stylistName: b.stylist?.name || '設計師',
        status: b.status,
        note: b.customer_note
      }))
    }
  } catch (error) {
    console.error('Failed to load calendar data:', error)
  } finally {
    loading.value = false
  }
}

// 載入設計師
const loadStylists = async () => {
  try {
    const res = await adminApi.getStylists()
    if (res.success && res.data) {
      stylists.value = res.data.map((s: AdminStylist) => ({
        id: s.id,
        name: s.name,
        isActive: s.is_active
      }))
    }
  } catch (error) {
    console.error('Failed to load stylists:', error)
  }
}

// 初始載入
onMounted(() => {
  loadCalendarData()
  loadStylists()
})

// 更新預約狀態
const updateBookingStatusAction = async (bookingId: string, status: BookingStatus) => {
  try {
    const res = await adminApi.updateBookingStatus(bookingId, status)
    if (res.success) {
      // 重新載入日曆資料
      await loadCalendarData()
    }
  } catch (error) {
    console.error('Failed to update booking status:', error)
  }
}

// 篩選狀態
const selectedStylist = ref('')
const selectedStatus = ref('')
const showBookingModal = ref(false)
const selectedBooking = ref<LocalBooking | null>(null)

// 設計師選項
const stylistOptions = computed(() => [
  { value: '', label: '全部設計師' },
  ...stylists.value
    .filter(s => s.isActive)
    .map(s => ({ value: s.id, label: s.name }))
])

// 狀態選項
const statusOptions = [
  { value: '', label: '全部狀態' },
  { value: 'pending', label: '待確認' },
  { value: 'confirmed', label: '已確認' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled_by_customer', label: '顧客取消' },
  { value: 'cancelled_by_salon', label: '店家取消' },
  { value: 'no_show', label: '未出席' }
]

// 狀態標籤對應
const statusLabels: Record<BookingStatus, string> = {
  pending: '待確認',
  confirmed: '已確認',
  completed: '已完成',
  cancelled_by_customer: '顧客取消',
  cancelled_by_salon: '店家取消',
  no_show: '未出席'
}

// 狀態樣式對應
const statusVariants: Record<BookingStatus, 'default' | 'primary' | 'success' | 'warning' | 'error'> = {
  pending: 'warning',
  confirmed: 'success',
  completed: 'primary',
  cancelled_by_customer: 'default',
  cancelled_by_salon: 'default',
  no_show: 'error'
}

// 篩選後的預約
const filteredBookings = computed(() => {
  return bookings.value.filter(booking => {
    if (selectedStylist.value && booking.stylistId !== selectedStylist.value) {
      return false
    }
    if (selectedStatus.value && booking.status !== selectedStatus.value) {
      return false
    }
    return true
  })
})

// 取得狀態標籤
const getStatusLabel = (status: BookingStatus): string => {
  return statusLabels[status] || status
}

// 取得狀態樣式
const getStatusVariant = (status: BookingStatus) => {
  return statusVariants[status] || 'default'
}

// 格式化日期
const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  const weekDays = ['日', '一', '二', '三', '四', '五', '六']
  const weekDay = weekDays[date.getDay()]
  return `${year}/${month}/${day}（${weekDay}）`
}

// 判斷是否可以變更狀態
const canChangeStatus = (status: BookingStatus): boolean => {
  return status === 'pending' || status === 'confirmed'
}

// 事件處理
const handleEventClick = (event: LocalBooking) => {
  selectedBooking.value = event
  showBookingModal.value = true
}

const handleDateClick = (dateStr: string) => {
  console.log('Date clicked:', dateStr)
}

const handleViewChange = (view: string) => {
  console.log('View changed:', view)
}

// 導航
const goToBookings = () => {
  router.push('/admin/bookings')
}

const handleAddBooking = () => {
  alert('尚未實作：新增預約\n\n此功能將在後續版本中提供。')
}

// 狀態變更操作
const confirmBooking = async () => {
  if (selectedBooking.value) {
    await updateBookingStatusAction(selectedBooking.value.id, 'confirmed')
    showBookingModal.value = false
  }
}

const completeBooking = async () => {
  if (selectedBooking.value) {
    await updateBookingStatusAction(selectedBooking.value.id, 'completed')
    showBookingModal.value = false
  }
}

const markNoShow = async () => {
  if (selectedBooking.value && confirm('確定要將此預約標記為未出席嗎？此操作會影響顧客的爽約紀錄。')) {
    await updateBookingStatusAction(selectedBooking.value.id, 'no_show')
    showBookingModal.value = false
  }
}

const cancelBooking = async () => {
  if (selectedBooking.value && confirm('確定要取消此預約嗎？')) {
    await updateBookingStatusAction(selectedBooking.value.id, 'cancelled_by_salon')
    showBookingModal.value = false
  }
}
</script>

<style scoped>
.admin-calendar-page {
  max-width: 1400px;
  margin: 0 auto;
}

/* 篩選列 */
.calendar-filters {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
  align-items: flex-end;
  padding: var(--spacing-md);
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  margin-bottom: var(--spacing-lg);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  min-width: 160px;
}

.filter-group label {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
}

/* 日曆容器 */
.calendar-wrapper {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  overflow: hidden;
}

/* 預約詳情 */
.booking-detail {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.booking-detail__row {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
}

.booking-detail__label {
  flex-shrink: 0;
  width: 80px;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.booking-detail__value {
  flex: 1;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.booking-detail__note {
  white-space: pre-wrap;
  background-color: var(--color-bg);
  padding: var(--spacing-sm);
  border-radius: var(--radius-md);
}

.booking-detail__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-light);
}

/* 響應式 */
@media (max-width: 768px) {
  .calendar-filters {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group {
    min-width: auto;
  }
}
</style>
