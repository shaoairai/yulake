<template>
  <!-- 廠商後台 - 顧客與黑名單管理 -->
  <div class="admin-customers">
    <!-- 頁面標題 -->
    <AdminPageHeader
      title="顧客與黑名單"
      description="查看顧客歷史紀錄與爽約次數，可將特定顧客加入黑名單。"
    />

    <!-- 搜尋與篩選區 -->
    <div class="admin-filters">
      <div class="filter-group" style="flex: 1;">
        <label>搜尋顧客</label>
        <AppInput
          v-model="searchKeyword"
          placeholder="輸入姓名或手機號碼"
          clearable
        />
      </div>
      <div class="filter-group">
        <label>&nbsp;</label>
        <label class="checkbox-label">
          <input
            v-model="showBlacklistOnly"
            type="checkbox"
            class="checkbox-input"
          >
          <span>只顯示黑名單</span>
        </label>
      </div>
    </div>

    <!-- 顧客列表 -->
    <AppCard no-padding>
      <div class="table-wrapper">
        <table class="table">
          <thead>
            <tr>
              <th>顧客</th>
              <th>總預約次數</th>
              <th>爽約次數</th>
              <th>狀態</th>
              <th>最後預約</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="customer in filteredCustomers" :key="customer.id">
              <td>
                <div class="customer-info">
                  <span class="customer-name">{{ customer.name }}</span>
                  <span class="customer-phone">{{ customer.phone }}</span>
                </div>
              </td>
              <td>{{ customer.totalBookings }}</td>
              <td>
                <span :class="{ 'text-error': customer.noShowCount > 0 }">
                  {{ customer.noShowCount }}
                </span>
              </td>
              <td>
                <AppBadge
                  :variant="customer.isBlacklisted ? 'error' : 'success'"
                  dot
                >
                  {{ customer.isBlacklisted ? '黑名單' : '正常' }}
                </AppBadge>
              </td>
              <td>{{ formatDate(customer.lastVisit) }}</td>
              <td>
                <AppButton variant="ghost" size="sm" @click="viewCustomerDetail(customer)">
                  查看詳情
                </AppButton>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 無資料狀態 -->
      <div v-if="filteredCustomers.length === 0" class="admin-empty-state">
        <span class="empty-icon">👥</span>
        <p class="empty-title">沒有符合條件的顧客</p>
        <p class="empty-description">請嘗試調整搜尋條件</p>
      </div>
    </AppCard>

    <!-- 顧客詳情 Modal -->
    <AppModal
      v-model="showDetailModal"
      title="顧客詳情"
      size="lg"
    >
      <div v-if="selectedCustomer" class="customer-detail">
        <!-- 基本資料 -->
        <div class="detail-section">
          <h4>基本資料</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">姓名</span>
              <span class="detail-value">{{ selectedCustomer.name }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">手機</span>
              <span class="detail-value">{{ selectedCustomer.phone }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">加入日期</span>
              <span class="detail-value">{{ formatDate(selectedCustomer.createdAt) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">最後預約</span>
              <span class="detail-value">{{ formatDate(selectedCustomer.lastVisit) }}</span>
            </div>
          </div>
        </div>

        <!-- 統計資訊 -->
        <div class="detail-section">
          <h4>統計資訊</h4>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-value">{{ selectedCustomer.totalBookings }}</span>
              <span class="stat-label">總預約次數</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ selectedCustomer.completedBookings }}</span>
              <span class="stat-label">已完成次數</span>
            </div>
            <div class="stat-item">
              <span class="stat-value text-error">{{ selectedCustomer.noShowCount }}</span>
              <span class="stat-label">爽約次數</span>
            </div>
          </div>
        </div>

        <!-- 預約歷史 -->
        <div class="detail-section">
          <h4>最近預約紀錄</h4>
          <div v-if="customerBookings.length > 0" class="history-list">
            <div
              v-for="booking in customerBookings"
              :key="booking.id"
              class="history-item"
            >
              <span class="history-date">{{ formatDate(booking.date) }}</span>
              <span class="history-service">{{ booking.serviceName }}</span>
              <AppBadge :variant="getStatusVariant(booking.status)" size="sm">
                {{ getStatusLabel(booking.status) }}
              </AppBadge>
            </div>
          </div>
          <p v-else class="no-history">尚無預約紀錄</p>
        </div>

        <!-- 店家備註 -->
        <div class="detail-section">
          <h4>店家備註</h4>
          <div class="note-edit">
            <textarea
              v-model="editingNote"
              class="note-textarea"
              placeholder="輸入顧客備註（如：喜好風格、注意事項等）"
              rows="3"
            ></textarea>
            <AppButton variant="secondary" size="sm" @click="saveNote">
              儲存備註
            </AppButton>
          </div>
        </div>

        <!-- 黑名單操作 -->
        <div class="detail-section">
          <h4>黑名單管理</h4>
          <div class="blacklist-action">
            <div class="blacklist-status">
              <span>目前狀態：</span>
              <AppBadge
                :variant="selectedCustomer.isBlacklisted ? 'error' : 'success'"
              >
                {{ selectedCustomer.isBlacklisted ? '已加入黑名單' : '正常' }}
              </AppBadge>
            </div>
            <AppButton
              v-if="selectedCustomer.isBlacklisted"
              variant="outline"
              @click="handleToggleBlacklist"
            >
              解除黑名單
            </AppButton>
            <AppButton
              v-else
              variant="danger"
              @click="handleToggleBlacklist"
            >
              加入黑名單
            </AppButton>
          </div>
          <p class="blacklist-hint">
            {{ selectedCustomer.isBlacklisted
              ? '解除黑名單後，該顧客將可以再次進行線上預約。'
              : '加入黑名單後，該顧客將無法透過線上系統預約本店服務。'
            }}
          </p>
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
 * 廠商後台 - 顧客與黑名單管理頁面
 * 提供顧客的查詢、備註編輯與黑名單管理
 */
import { ref, computed, onMounted } from 'vue'
import { useAdminApi } from '~/composables/useAdminApi'
import type { BookingStatus, AdminCustomer, AdminBooking } from '~/composables/useAdminApi'

// 設定使用 admin layout 與認證
definePageMeta({
  layout: 'admin',
  middleware: 'auth'
})

// API
const adminApi = useAdminApi()

// 本地狀態
const loading = ref(false)

// 本地顧客介面（保持 template 相容）
interface LocalCustomer {
  id: string
  name: string
  phone: string
  email: string
  totalBookings: number
  completedBookings: number
  noShowCount: number
  isBlacklisted: boolean
  note: string
  lastVisit: string
  createdAt: string
}

const customers = ref<LocalCustomer[]>([])

// 本地預約介面
interface LocalBooking {
  id: string
  customerId: string
  date: string
  serviceName: string
  status: BookingStatus
}

const bookings = ref<LocalBooking[]>([])

// 載入顧客資料
const loadCustomers = async () => {
  loading.value = true
  try {
    const res = await adminApi.getCustomers()
    if (res.success && res.data) {
      customers.value = res.data.map((c: AdminCustomer) => ({
        id: c.id,
        name: c.name,
        phone: c.phone || '',
        email: c.email,
        totalBookings: c.stats?.total_bookings || 0,
        completedBookings: c.stats?.completed_bookings || 0,
        noShowCount: c.stats?.no_show_count || 0,
        isBlacklisted: c.salon_relation?.is_blacklisted || false,
        note: c.salon_relation?.note || '',
        lastVisit: c.salon_relation?.last_visit_at || '',
        createdAt: c.created_at
      }))
    }
  } catch (error) {
    console.error('Failed to load customers:', error)
  } finally {
    loading.value = false
  }
}

// 載入預約紀錄（用於顧客詳情）
const loadCustomerBookings = async (customerId: string) => {
  try {
    // 從 API 取得該顧客的預約（簡化處理，實際可加 customer_id 參數）
    const res = await adminApi.getBookings()
    if (res.success && res.data) {
      bookings.value = res.data
        .filter((b: AdminBooking) => b.customer?.id === customerId)
        .map((b: AdminBooking) => ({
          id: b.id,
          customerId: b.customer?.id || '',
          date: b.booking_date,
          serviceName: b.service?.name || '服務',
          status: b.status
        }))
    }
  } catch (error) {
    console.error('Failed to load bookings:', error)
  }
}

// 初始載入
onMounted(() => {
  loadCustomers()
})

// 更新顧客備註
const updateCustomerNoteAction = async (customerId: string, note: string) => {
  try {
    const res = await adminApi.updateCustomerNote(customerId, note)
    if (res.success) {
      // 更新本地資料
      const customer = customers.value.find(c => c.id === customerId)
      if (customer) {
        customer.note = note
      }
    }
  } catch (error) {
    console.error('Failed to update customer note:', error)
  }
}

// 切換黑名單狀態
const toggleCustomerBlacklistAction = async (customerId: string, isBlacklisted: boolean) => {
  try {
    if (isBlacklisted) {
      await adminApi.removeFromBlacklist(customerId)
    } else {
      await adminApi.addToBlacklist(customerId, '店家加入')
    }
    // 重新載入顧客資料
    await loadCustomers()
  } catch (error) {
    console.error('Failed to toggle blacklist:', error)
  }
}

// 搜尋關鍵字
const searchKeyword = ref('')

// 只顯示黑名單
const showBlacklistOnly = ref(false)

// 詳情 Modal 狀態
const showDetailModal = ref(false)
const selectedCustomer = ref<LocalCustomer | null>(null)
const editingNote = ref('')

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

// 篩選後的顧客列表
const filteredCustomers = computed(() => {
  return customers.value.filter(customer => {
    // 黑名單篩選
    if (showBlacklistOnly.value && !customer.isBlacklisted) {
      return false
    }
    // 關鍵字搜尋
    if (searchKeyword.value) {
      const keyword = searchKeyword.value.toLowerCase()
      const nameMatch = customer.name.toLowerCase().includes(keyword)
      const phoneMatch = customer.phone.replace(/-/g, '').includes(keyword.replace(/-/g, ''))
      if (!nameMatch && !phoneMatch) {
        return false
      }
    }
    return true
  })
})

// 選中顧客的預約紀錄
const customerBookings = computed(() => {
  if (!selectedCustomer.value) return []
  return bookings.value
    .filter(b => b.customerId === selectedCustomer.value!.id)
    .sort((a, b) => b.date.localeCompare(a.date))
    .slice(0, 5)
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
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`
}

// 查看顧客詳情
const viewCustomerDetail = async (customer: LocalCustomer) => {
  selectedCustomer.value = customer
  editingNote.value = customer.note
  showDetailModal.value = true
  // 載入該顧客的預約紀錄
  await loadCustomerBookings(customer.id)
}

// 儲存備註
const saveNote = async () => {
  if (selectedCustomer.value) {
    await updateCustomerNoteAction(selectedCustomer.value.id, editingNote.value)
    alert('備註已儲存')
  }
}

// 切換黑名單狀態
const handleToggleBlacklist = async () => {
  if (!selectedCustomer.value) return

  const action = selectedCustomer.value.isBlacklisted ? '解除' : '加入'
  const message = selectedCustomer.value.isBlacklisted
    ? `確定要將「${selectedCustomer.value.name}」從黑名單中移除嗎？`
    : `確定要將「${selectedCustomer.value.name}」加入黑名單嗎？\n\n加入後該顧客將無法使用線上預約。`

  if (confirm(message)) {
    await toggleCustomerBlacklistAction(selectedCustomer.value.id, selectedCustomer.value.isBlacklisted)
    // 更新 selectedCustomer 的狀態
    selectedCustomer.value.isBlacklisted = !selectedCustomer.value.isBlacklisted
    alert(`已${action}黑名單`)
  }
}
</script>

<style scoped>
.admin-customers {
  max-width: 1200px;
  margin: 0 auto;
}

/* 顧客資訊 */
.customer-info {
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

/* Checkbox 樣式 */
.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  height: 40px;
  cursor: pointer;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.checkbox-input {
  width: 18px;
  height: 18px;
  accent-color: var(--color-primary);
}

/* 顧客詳情 Modal */
.customer-detail {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.detail-section h4 {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-secondary);
  margin: 0;
  padding-bottom: var(--spacing-xs);
  border-bottom: 1px solid var(--color-border-light);
}

/* 詳情網格 */
.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-md);
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.detail-value {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-primary);
}

/* 統計網格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: var(--spacing-md);
  background: var(--color-bg);
  border-radius: var(--radius-md);
}

.stat-value {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--color-text-primary);
}

.stat-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

/* 歷史紀錄 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.history-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm);
  background: var(--color-bg);
  border-radius: var(--radius-md);
}

.history-date {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-primary);
  min-width: 100px;
}

.history-service {
  flex: 1;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.no-history {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  text-align: center;
  padding: var(--spacing-md);
  margin: 0;
}

/* 備註編輯 */
.note-edit {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.note-textarea {
  width: 100%;
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: inherit;
  font-size: var(--font-size-sm);
  resize: vertical;
  outline: none;
  transition: border-color var(--transition-fast);
}

.note-textarea:focus {
  border-color: var(--color-primary);
}

/* 黑名單操作 */
.blacklist-action {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);
}

.blacklist-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.blacklist-hint {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  margin: 0;
}

/* 響應式 */
@media (max-width: 768px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .blacklist-action {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
