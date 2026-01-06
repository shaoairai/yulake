<template>
  <!-- 廠商後台 - 店家設定 -->
  <div class="admin-settings">
    <!-- 頁面標題 -->
    <AdminPageHeader
      title="店家設定"
      description="設定店家基本資訊與預約相關連結。"
    />

    <div class="settings-grid">
      <!-- 店家基本資料 -->
      <AppCard title="店家基本資料">
        <form class="settings-form" @submit.prevent="saveBasicInfo">
          <div class="form-group">
            <label class="form-label">店家名稱</label>
            <AppInput v-model="formData.name" placeholder="輸入店家名稱" />
          </div>

          <div class="form-group">
            <label class="form-label">地址</label>
            <AppInput v-model="formData.address" placeholder="輸入店家地址" />
          </div>

          <div class="form-group">
            <label class="form-label">電話</label>
            <AppInput v-model="formData.phone" placeholder="例如：02-2771-1234" />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">LINE 官方帳號</label>
              <AppInput v-model="formData.lineId" placeholder="例如：@shop_name" />
            </div>

            <div class="form-group">
              <label class="form-label">Instagram 帳號</label>
              <AppInput v-model="formData.igAccount" placeholder="例如：shop_name" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">官方網站</label>
            <AppInput v-model="formData.website" placeholder="https://your-website.com" />
          </div>

          <div class="form-actions">
            <AppButton variant="primary" type="submit">
              儲存變更
            </AppButton>
          </div>
        </form>
      </AppCard>

      <!-- 營業時間 -->
      <AppCard title="營業時間">
        <div class="business-hours">
          <div
            v-for="hour in salon.businessHours"
            :key="hour.day"
            class="hours-row"
          >
            <span class="hours-day">{{ hour.day }}</span>
            <span v-if="hour.isOpen" class="hours-time">
              {{ hour.openTime }} - {{ hour.closeTime }}
            </span>
            <span v-else class="hours-closed">公休</span>
          </div>
        </div>
        <p class="hours-hint">
          營業時間編輯功能將於之後版本提供
        </p>
      </AppCard>

      <!-- 預約連結 -->
      <AppCard title="預約連結" class="booking-link-card">
        <div class="booking-link-section">
          <p class="booking-link-description">
            請將此連結放入你的 WordPress 官網按鈕、IG 連結、LINE 選單，顧客即可直接進入預約流程。
          </p>

          <div class="booking-link-box">
            <span class="booking-link-url">{{ salon.bookingUrl }}</span>
            <AppButton variant="secondary" size="sm" @click="copyBookingLink">
              複製連結
            </AppButton>
          </div>

          <div class="qr-section">
            <div class="qr-placeholder">
              <span class="qr-icon">📱</span>
              <span class="qr-text">QR Code</span>
            </div>
            <p class="qr-hint">
              QR Code 下載功能將於之後版本提供
            </p>
          </div>
        </div>
      </AppCard>

      <!-- 預約規則 -->
      <AppCard title="預約規則">
        <div class="rules-list">
          <div class="rule-item">
            <span class="rule-label">預約間隔</span>
            <span class="rule-value">{{ bookingRule.slotInterval }} 分鐘</span>
          </div>
          <div class="rule-item">
            <span class="rule-label">最晚預約時間</span>
            <span class="rule-value">至少提前 {{ bookingRule.minAdvanceHours }} 小時</span>
          </div>
          <div class="rule-item">
            <span class="rule-label">可預約天數</span>
            <span class="rule-value">未來 {{ bookingRule.maxAdvanceDays }} 天</span>
          </div>
          <div class="rule-item">
            <span class="rule-label">預約確認方式</span>
            <span class="rule-value">{{ bookingRule.requireConfirmation ? '需店家確認' : '自動確認' }}</span>
          </div>
        </div>
        <p class="rules-hint">
          預約規則編輯功能將於之後版本提供
        </p>
      </AppCard>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 廠商後台 - 店家設定頁面
 * 提供店家基本資料與預約連結管理
 */
import { ref, reactive, onMounted } from 'vue'
import { useAdminApi } from '~/composables/useAdminApi'
import type { SalonSettings } from '~/composables/useAdminApi'

// 設定使用 admin layout 與認證
definePageMeta({
  layout: 'admin',
  middleware: 'auth'
})

// API
const adminApi = useAdminApi()

// 本地狀態
const loading = ref(false)

// 店家資料（保持 template 相容）
const salon = reactive({
  name: '',
  address: '',
  phone: '',
  lineId: '',
  igAccount: '',
  website: '',
  bookingUrl: '',
  businessHours: [] as { day: string; isOpen: boolean; openTime: string; closeTime: string }[]
})

// 預約規則
const bookingRule = reactive({
  slotInterval: 30,
  minAdvanceHours: 3,
  maxAdvanceDays: 30,
  requireConfirmation: false
})

// 表單資料
const formData = reactive({
  name: '',
  address: '',
  phone: '',
  lineId: '',
  igAccount: '',
  website: ''
})

// 星期對應
const dayNames = ['週日', '週一', '週二', '週三', '週四', '週五', '週六']

// 載入設定
const loadSettings = async () => {
  loading.value = true
  try {
    const res = await adminApi.getSettings()
    if (res.success && res.data) {
      const data = res.data as SalonSettings

      // 更新店家資料
      salon.name = data.salon.name
      salon.address = data.salon.address
      salon.phone = data.salon.phone
      salon.lineId = data.salon.line_id || ''
      salon.igAccount = data.salon.ig_account || ''
      salon.website = data.salon.website || ''
      salon.bookingUrl = data.salon.booking_url

      // 轉換營業時間格式
      salon.businessHours = data.business_hours.map(h => ({
        day: dayNames[h.day_of_week],
        isOpen: h.is_open,
        openTime: h.open_time || '',
        closeTime: h.close_time || ''
      }))

      // 更新預約規則
      if (data.booking_rule) {
        bookingRule.slotInterval = data.booking_rule.slot_interval
        bookingRule.minAdvanceHours = data.booking_rule.min_advance_hours
        bookingRule.maxAdvanceDays = data.booking_rule.max_advance_days
        bookingRule.requireConfirmation = data.booking_rule.require_confirmation
      }

      // 同步表單資料
      formData.name = salon.name
      formData.address = salon.address
      formData.phone = salon.phone
      formData.lineId = salon.lineId
      formData.igAccount = salon.igAccount
      formData.website = salon.website
    }
  } catch (error) {
    console.error('Failed to load settings:', error)
  } finally {
    loading.value = false
  }
}

// 初始載入
onMounted(() => {
  loadSettings()
})

// 儲存基本資料
const saveBasicInfo = async () => {
  try {
    const res = await adminApi.updateSettings({
      name: formData.name,
      address: formData.address,
      phone: formData.phone,
      line_id: formData.lineId,
      ig_account: formData.igAccount,
      website: formData.website
    })
    if (res.success) {
      // 同步本地資料
      salon.name = formData.name
      salon.address = formData.address
      salon.phone = formData.phone
      salon.lineId = formData.lineId
      salon.igAccount = formData.igAccount
      salon.website = formData.website
      alert('店家資料已儲存')
    }
  } catch (error) {
    console.error('Failed to save settings:', error)
    alert('儲存失敗，請稍後再試')
  }
}

// 複製預約連結
const copyBookingLink = async () => {
  try {
    await navigator.clipboard.writeText(salon.bookingUrl)
    alert('預約連結已複製到剪貼簿')
  } catch {
    // 如果 clipboard API 不支援，使用傳統方式
    const textArea = document.createElement('textarea')
    textArea.value = salon.bookingUrl
    document.body.appendChild(textArea)
    textArea.select()
    try {
      document.execCommand('copy')
      alert('預約連結已複製到剪貼簿')
    } catch {
      alert(`請手動複製連結：${salon.bookingUrl}`)
    }
    document.body.removeChild(textArea)
  }
}
</script>

<style scoped>
.admin-settings {
  max-width: 1200px;
  margin: 0 auto;
}

/* 設定網格 */
.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-lg);
}

/* 表單樣式 */
.settings-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.form-label {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-primary);
}

.form-actions {
  margin-top: var(--spacing-sm);
}

/* 營業時間 */
.business-hours {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.hours-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-sm);
  background: var(--color-bg);
  border-radius: var(--radius-md);
}

.hours-day {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-primary);
  min-width: 40px;
}

.hours-time {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.hours-closed {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.hours-hint {
  margin-top: var(--spacing-md);
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

/* 預約連結 */
.booking-link-card {
  grid-column: 1 / -1;
}

.booking-link-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.booking-link-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

.booking-link-box {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: var(--color-primary-light);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-primary);
}

.booking-link-url {
  flex: 1;
  font-size: var(--font-size-sm);
  font-family: monospace;
  color: var(--color-primary);
  word-break: break-all;
}

.qr-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.qr-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 120px;
  height: 120px;
  background: var(--color-bg);
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-md);
}

.qr-icon {
  font-size: 32px;
  margin-bottom: var(--spacing-xs);
}

.qr-text {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.qr-hint {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  margin: 0;
}

/* 預約規則 */
.rules-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.rule-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-sm);
  background: var(--color-bg);
  border-radius: var(--radius-md);
}

.rule-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.rule-value {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-primary);
}

.rules-hint {
  margin-top: var(--spacing-md);
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

/* 響應式 */
@media (max-width: 1024px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }

  .booking-link-card {
    grid-column: auto;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
