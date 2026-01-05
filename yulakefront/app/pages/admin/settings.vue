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
            <span class="rule-value">30 分鐘</span>
          </div>
          <div class="rule-item">
            <span class="rule-label">最晚預約時間</span>
            <span class="rule-value">至少提前 3 小時</span>
          </div>
          <div class="rule-item">
            <span class="rule-label">可預約天數</span>
            <span class="rule-value">未來 30 天</span>
          </div>
          <div class="rule-item">
            <span class="rule-label">預約確認方式</span>
            <span class="rule-value">自動確認</span>
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
import { reactive } from 'vue'
import { useAdminMockData } from '~/composables/useAdminMockData'

// 設定使用 admin layout
definePageMeta({
  layout: 'admin'
})

// 取得假資料
const { salon, updateSalon } = useAdminMockData()

// 表單資料
const formData = reactive({
  name: salon.name,
  address: salon.address,
  phone: salon.phone,
  lineId: salon.lineId,
  igAccount: salon.igAccount,
  website: salon.website
})

// 儲存基本資料
const saveBasicInfo = () => {
  updateSalon({
    name: formData.name,
    address: formData.address,
    phone: formData.phone,
    lineId: formData.lineId,
    igAccount: formData.igAccount,
    website: formData.website
  })
  alert('店家資料已儲存')
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
