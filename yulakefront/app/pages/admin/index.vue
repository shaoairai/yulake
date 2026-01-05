<template>
  <!-- 廠商後台 - 今日總覽 Dashboard -->
  <div class="admin-dashboard">
    <!-- 頁面標題 -->
    <AdminPageHeader
      title="今日總覽"
      description="查看今日預約與關鍵數據指標"
    />

    <!-- 統計卡片列 -->
    <section class="admin-dashboard__stats">
      <AdminStatCard
        title="本週預約總數"
        :value="stats.weeklyBookings"
        :subtitle="`較上週 ${stats.weeklyBookingsChange}`"
        icon="📅"
        variant="primary"
      />
      <AdminStatCard
        title="爽約次數"
        :value="stats.noShowCount"
        :subtitle="`較上週 ${stats.noShowCountChange}`"
        icon="⚠️"
        variant="warning"
      />
      <AdminStatCard
        title="新顧客數"
        :value="stats.newCustomers"
        :subtitle="`較上週 ${stats.newCustomersChange}`"
        icon="👤"
        variant="success"
      />
    </section>

    <!-- 今日預約列表 -->
    <section class="admin-dashboard__bookings">
      <AppCard title="今日預約" :subtitle="`共 ${todayBookings.length} 筆`">
        <template #headerAction>
          <AppButton variant="ghost" size="sm" @click="goToBookings">
            查看全部
          </AppButton>
        </template>

        <!-- 預約列表 -->
        <div v-if="todayBookings.length > 0" class="booking-list">
          <div
            v-for="booking in todayBookings"
            :key="booking.id"
            class="booking-item"
          >
            <div class="booking-item__time">
              {{ booking.startTime }}
            </div>
            <div class="booking-item__info">
              <span class="booking-item__customer">{{ booking.customerName }}</span>
              <span class="booking-item__service">{{ booking.serviceName }}</span>
            </div>
            <div class="booking-item__stylist">
              {{ booking.stylistName }}
            </div>
            <div class="booking-item__status">
              <AppBadge :variant="getStatusVariant(booking.status)">
                {{ getStatusLabel(booking.status) }}
              </AppBadge>
            </div>
          </div>
        </div>

        <!-- 無預約狀態 -->
        <div v-else class="admin-empty-state">
          <span class="empty-icon">📅</span>
          <p class="empty-title">今日沒有預約</p>
          <p class="empty-description">可以在預約管理中新增預約</p>
        </div>
      </AppCard>
    </section>

    <!-- 底部卡片列 -->
    <section class="admin-dashboard__bottom">
      <!-- 快速操作 -->
      <AppCard title="快速操作">
        <div class="quick-actions">
          <AppButton variant="primary" @click="handleAddBooking">
            ＋ 新增預約
          </AppButton>
          <AppButton variant="outline" @click="handleOpenCalendar">
            📆 開啟行事曆
          </AppButton>
        </div>
      </AppCard>

      <!-- 回訪與生日提醒 -->
      <AppCard title="回訪與生日提醒">
        <div v-if="reminders.length > 0" class="reminder-list">
          <div
            v-for="reminder in reminders"
            :key="reminder.id"
            class="reminder-item"
          >
            <span class="reminder-item__icon">
              {{ reminder.type === 'birthday' ? '🎂' : '⏰' }}
            </span>
            <div class="reminder-item__info">
              <span class="reminder-item__name">{{ reminder.customerName }}</span>
              <span class="reminder-item__type">
                {{ reminder.type === 'birthday' ? '生日' : '建議回訪' }}
              </span>
            </div>
            <span class="reminder-item__date">{{ formatReminderDate(reminder.date) }}</span>
          </div>
        </div>
        <div v-else class="admin-empty-state">
          <span class="empty-icon">🔔</span>
          <p class="empty-description">目前沒有提醒</p>
        </div>
      </AppCard>
    </section>
  </div>
</template>

<script setup lang="ts">
/**
 * 廠商後台 - 今日總覽頁面
 * 顯示統計數據、今日預約與快速操作
 */
import { useRouter } from 'vue-router'
import { useAdminMockData } from '~/composables/useAdminMockData'
import type { BookingStatus } from '~/composables/useAdminMockData'

// 設定使用 admin layout
definePageMeta({
  layout: 'admin'
})

// 路由
const router = useRouter()

// 取得假資料
const { stats, todayBookings, reminders } = useAdminMockData()

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

// 取得狀態標籤
const getStatusLabel = (status: BookingStatus): string => {
  return statusLabels[status] || status
}

// 取得狀態樣式
const getStatusVariant = (status: BookingStatus) => {
  return statusVariants[status] || 'default'
}

// 格式化提醒日期
const formatReminderDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${month}/${day}`
}

// 跳轉到預約管理
const goToBookings = () => {
  router.push('/admin/bookings')
}

// 新增預約（尚未實作）
const handleAddBooking = () => {
  alert('尚未實作：新增預約\n\n此功能將在後續版本中提供。')
}

// 開啟行事曆
const handleOpenCalendar = () => {
  router.push('/admin/calendar')
}
</script>

<style scoped>
.admin-dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

/* 統計卡片列 */
.admin-dashboard__stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

/* 今日預約區塊 */
.admin-dashboard__bookings {
  margin-bottom: var(--spacing-xl);
}

/* 預約列表 */
.booking-list {
  display: flex;
  flex-direction: column;
}

.booking-item {
  display: grid;
  grid-template-columns: 60px 1fr 100px 100px;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) 0;
  border-bottom: 1px solid var(--color-border-light);
}

.booking-item:last-child {
  border-bottom: none;
}

.booking-item__time {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-primary);
}

.booking-item__info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.booking-item__customer {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-primary);
}

.booking-item__service {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.booking-item__stylist {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.booking-item__status {
  text-align: right;
}

/* 底部卡片列 */
.admin-dashboard__bottom {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
}

/* 快速操作 */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

/* 提醒列表 */
.reminder-list {
  display: flex;
  flex-direction: column;
}

.reminder-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--color-border-light);
}

.reminder-item:last-child {
  border-bottom: none;
}

.reminder-item__icon {
  font-size: var(--font-size-lg);
}

.reminder-item__info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.reminder-item__name {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-primary);
}

.reminder-item__type {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.reminder-item__date {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

/* 響應式 */
@media (max-width: 1024px) {
  .admin-dashboard__stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .admin-dashboard__bottom {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .admin-dashboard__stats {
    grid-template-columns: 1fr;
  }

  .booking-item {
    grid-template-columns: 50px 1fr;
    gap: var(--spacing-sm);
  }

  .booking-item__stylist,
  .booking-item__status {
    grid-column: 2;
  }
}
</style>
