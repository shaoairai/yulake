<template>
  <!-- 廠商後台 - 預約管理 -->
  <div class="admin-bookings">
    <!-- 頁面標題 -->
    <AdminPageHeader
      title="預約管理"
      description="查看與管理所有預約紀錄，可依日期、設計師與狀態篩選。"
    >
      <template #actions>
        <AppButton variant="primary" @click="handleAddBooking">
          ＋ 新增預約
        </AppButton>
      </template>
    </AdminPageHeader>

    <!-- 篩選區 -->
    <div class="admin-filters">
      <div class="filter-group">
        <label>開始日期</label>
        <AppInput
          v-model="filters.dateRange.startDate"
          type="date"
        />
      </div>
      <div class="filter-group">
        <label>結束日期</label>
        <AppInput
          v-model="filters.dateRange.endDate"
          type="date"
        />
      </div>
      <div class="filter-group">
        <label>設計師</label>
        <AppSelect
          v-model="filters.stylistId"
          :options="stylistOptions"
          placeholder="全部設計師"
        />
      </div>
      <div class="filter-group">
        <label>狀態</label>
        <AppSelect
          v-model="filters.status"
          :options="statusOptions"
          placeholder="全部狀態"
        />
      </div>
      <div class="filter-actions">
        <AppButton variant="secondary" size="sm" @click="applyFilters">
          套用篩選
        </AppButton>
        <AppButton variant="ghost" size="sm" @click="resetFilters">
          清除條件
        </AppButton>
      </div>
    </div>

    <!-- 預約列表 -->
    <AppCard no-padding>
      <div class="table-wrapper">
        <table class="table">
          <thead>
            <tr>
              <th>日期時間</th>
              <th>顧客</th>
              <th>服務</th>
              <th>設計師</th>
              <th>狀態</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="booking in filteredBookings" :key="booking.id">
              <td>
                <div class="booking-datetime">
                  <span class="booking-date">{{ formatDate(booking.date) }}</span>
                  <span class="booking-time">{{ booking.startTime }} - {{ booking.endTime }}</span>
                </div>
              </td>
              <td>
                <div class="booking-customer">
                  <span class="customer-name">{{ booking.customerName }}</span>
                  <span class="customer-phone">{{ booking.customerPhone }}</span>
                </div>
              </td>
              <td>{{ booking.serviceName }}</td>
              <td>{{ booking.stylistName }}</td>
              <td>
                <AppBadge :variant="getStatusVariant(booking.status)" dot>
                  {{ getStatusLabel(booking.status) }}
                </AppBadge>
              </td>
              <td>
                <div class="booking-actions">
                  <AppButton variant="ghost" size="sm" @click="viewBookingDetail(booking)">
                    查看
                  </AppButton>
                  <AppButton
                    v-if="booking.status === 'pending'"
                    variant="ghost"
                    size="sm"
                    @click="confirmBooking(booking.id)"
                  >
                    確認
                  </AppButton>
                  <AppButton
                    v-if="booking.status === 'confirmed'"
                    variant="ghost"
                    size="sm"
                    @click="completeBooking(booking.id)"
                  >
                    完成
                  </AppButton>
                  <AppButton
                    v-if="booking.status === 'confirmed'"
                    variant="ghost"
                    size="sm"
                    @click="markNoShow(booking.id)"
                  >
                    未出席
                  </AppButton>
                  <AppButton
                    v-if="booking.status === 'pending' || booking.status === 'confirmed'"
                    variant="ghost"
                    size="sm"
                    @click="cancelBooking(booking.id)"
                  >
                    取消
                  </AppButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 無資料狀態 -->
      <div v-if="filteredBookings.length === 0" class="admin-empty-state">
        <span class="empty-icon">📅</span>
        <p class="empty-title">沒有符合條件的預約</p>
        <p class="empty-description">請嘗試調整篩選條件</p>
      </div>
    </AppCard>

    <!-- 預約詳情 Modal -->
    <AppModal
      v-model="showDetailModal"
      title="預約詳情"
      size="md"
    >
      <div v-if="selectedBooking" class="booking-detail">
        <div class="detail-section">
          <h4>預約資訊</h4>
          <div class="detail-row">
            <span class="detail-label">日期</span>
            <span class="detail-value">{{ formatDate(selectedBooking.date) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">時間</span>
            <span class="detail-value">{{ selectedBooking.startTime }} - {{ selectedBooking.endTime }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">服務</span>
            <span class="detail-value">{{ selectedBooking.serviceName }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">設計師</span>
            <span class="detail-value">{{ selectedBooking.stylistName }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">狀態</span>
            <span class="detail-value">
              <AppBadge :variant="getStatusVariant(selectedBooking.status)">
                {{ getStatusLabel(selectedBooking.status) }}
              </AppBadge>
            </span>
          </div>
        </div>

        <div class="detail-section">
          <h4>顧客資訊</h4>
          <div class="detail-row">
            <span class="detail-label">姓名</span>
            <span class="detail-value">{{ selectedBooking.customerName }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">電話</span>
            <span class="detail-value">{{ selectedBooking.customerPhone }}</span>
          </div>
        </div>

        <div v-if="selectedBooking.note" class="detail-section">
          <h4>備註</h4>
          <p class="detail-note">{{ selectedBooking.note }}</p>
        </div>

        <div class="detail-section">
          <h4>建立時間</h4>
          <p class="detail-created">{{ selectedBooking.createdAt }}</p>
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
 * 廠商後台 - 預約管理頁面
 * 提供預約的查詢、篩選與狀態管理
 */
import { ref, computed } from 'vue'
import { useAdminMockData } from '~/composables/useAdminMockData'
import { useAdminState } from '~/composables/useAdminState'
import type { Booking, BookingStatus } from '~/composables/useAdminMockData'

// 設定使用 admin layout
definePageMeta({
  layout: 'admin'
})

// 取得假資料與狀態
const { bookings, stylists, updateBookingStatus } = useAdminMockData()
const { bookingFilters, resetBookingFilters } = useAdminState()

// 篩選條件（本地副本）
const filters = ref({
  dateRange: {
    startDate: bookingFilters.dateRange.startDate,
    endDate: bookingFilters.dateRange.endDate
  },
  stylistId: '',
  status: ''
})

// 設計師選項
const stylistOptions = computed(() => [
  { label: '全部設計師', value: '' },
  ...stylists.filter(s => s.isActive).map(s => ({
    label: s.name,
    value: s.id
  }))
])

// 狀態選項
const statusOptions = [
  { label: '全部狀態', value: '' },
  { label: '待確認', value: 'pending' },
  { label: '已確認', value: 'confirmed' },
  { label: '已完成', value: 'completed' },
  { label: '顧客取消', value: 'cancelled_by_customer' },
  { label: '店家取消', value: 'cancelled_by_salon' },
  { label: '未出席', value: 'no_show' }
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

// 篩選後的預約列表
const filteredBookings = computed(() => {
  return bookings.filter(booking => {
    // 日期範圍篩選
    if (filters.value.dateRange.startDate && booking.date < filters.value.dateRange.startDate) {
      return false
    }
    if (filters.value.dateRange.endDate && booking.date > filters.value.dateRange.endDate) {
      return false
    }
    // 設計師篩選
    if (filters.value.stylistId && booking.stylistId !== filters.value.stylistId) {
      return false
    }
    // 狀態篩選
    if (filters.value.status && booking.status !== filters.value.status) {
      return false
    }
    return true
  }).sort((a, b) => {
    // 按日期與時間排序
    const dateCompare = a.date.localeCompare(b.date)
    if (dateCompare !== 0) return dateCompare
    return a.startTime.localeCompare(b.startTime)
  })
})

// 詳情 Modal 狀態
const showDetailModal = ref(false)
const selectedBooking = ref<Booking | null>(null)

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
  const month = date.getMonth() + 1
  const day = date.getDate()
  const weekdays = ['日', '一', '二', '三', '四', '五', '六']
  const weekday = weekdays[date.getDay()]
  return `${month}/${day} (${weekday})`
}

// 套用篩選
const applyFilters = () => {
  // 篩選已經是響應式的，這裡可以加入其他邏輯
}

// 重置篩選
const resetFilters = () => {
  resetBookingFilters()
  filters.value = {
    dateRange: {
      startDate: '',
      endDate: ''
    },
    stylistId: '',
    status: ''
  }
}

// 查看預約詳情
const viewBookingDetail = (booking: Booking) => {
  selectedBooking.value = booking
  showDetailModal.value = true
}

// 確認預約
const confirmBooking = (bookingId: string) => {
  updateBookingStatus(bookingId, 'confirmed')
}

// 完成預約
const completeBooking = (bookingId: string) => {
  updateBookingStatus(bookingId, 'completed')
}

// 標記未出席
const markNoShow = (bookingId: string) => {
  if (confirm('確定要將此預約標記為「未出席」嗎？\n此操作會累計顧客的爽約次數。')) {
    updateBookingStatus(bookingId, 'no_show')
  }
}

// 取消預約
const cancelBooking = (bookingId: string) => {
  if (confirm('確定要取消此預約嗎？')) {
    updateBookingStatus(bookingId, 'cancelled_by_salon')
  }
}

// 新增預約（尚未實作）
const handleAddBooking = () => {
  alert('尚未實作：新增預約\n\n此功能將在後續版本中提供。')
}
</script>

<style scoped>
.admin-bookings {
  max-width: 1200px;
  margin: 0 auto;
}

/* 篩選區 */
.admin-filters {
  margin-bottom: var(--spacing-lg);
}

.filter-actions {
  display: flex;
  gap: var(--spacing-sm);
  align-items: flex-end;
}

/* 預約日期時間 */
.booking-datetime {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.booking-date {
  font-weight: 500;
  color: var(--color-text-primary);
}

.booking-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

/* 預約顧客 */
.booking-customer {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.customer-name {
  font-weight: 500;
  color: var(--color-text-primary);
}

.customer-phone {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

/* 預約操作按鈕 */
.booking-actions {
  display: flex;
  gap: var(--spacing-xs);
  flex-wrap: wrap;
}

/* 預約詳情 Modal */
.booking-detail {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.detail-section h4 {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-secondary);
  margin: 0;
  padding-bottom: var(--spacing-xs);
  border-bottom: 1px solid var(--color-border-light);
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.detail-value {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-primary);
}

.detail-note {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  background: var(--color-bg);
  padding: var(--spacing-sm);
  border-radius: var(--radius-md);
  margin: 0;
}

.detail-created {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin: 0;
}

/* 響應式 */
@media (max-width: 1024px) {
  .admin-filters {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group {
    width: 100%;
  }

  .filter-actions {
    margin-top: var(--spacing-sm);
  }
}

@media (max-width: 768px) {
  .table th:nth-child(3),
  .table td:nth-child(3),
  .table th:nth-child(4),
  .table td:nth-child(4) {
    display: none;
  }
}
</style>
