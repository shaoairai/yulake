<template>
  <!-- 廠商後台 - 自動發信設定 -->
  <div class="admin-automation">
    <!-- 頁面標題 -->
    <AdminPageHeader
      title="自動發信設定"
      description="設定自動發送的 Email 通知規則"
    >
      <template #actions>
        <AppButton variant="outline" size="sm" @click="goToMarketing">
          返回行銷總覽
        </AppButton>
      </template>
    </AdminPageHeader>

    <!-- 自動發信規則列表 -->
    <div class="rules-grid">
      <!-- 預約確認通知 -->
      <AppCard title="預約確認通知">
        <div class="rule-content">
          <div class="rule-description">
            當顧客預約成功確認後，自動發送確認通知 Email。
          </div>
          <div class="rule-toggle">
            <label class="toggle-label">
              <input
                v-model="rules.bookingConfirm.enabled"
                type="checkbox"
                class="toggle-input"
                @change="updateRule('bookingConfirm')"
              >
              <span class="toggle-switch" />
              <span class="toggle-text">{{ rules.bookingConfirm.enabled ? '已啟用' : '已停用' }}</span>
            </label>
          </div>
          <div v-if="rules.bookingConfirm.enabled" class="rule-settings">
            <div class="setting-item">
              <span class="setting-label">使用範本</span>
              <AppSelect
                v-model="rules.bookingConfirm.templateId"
                :options="bookingTemplateOptions"
                @change="updateRule('bookingConfirm')"
              />
            </div>
          </div>
        </div>
      </AppCard>

      <!-- 預約提醒通知 -->
      <AppCard title="預約提醒通知">
        <div class="rule-content">
          <div class="rule-description">
            在預約日期前自動發送提醒 Email 給顧客。
          </div>
          <div class="rule-toggle">
            <label class="toggle-label">
              <input
                v-model="rules.bookingReminder.enabled"
                type="checkbox"
                class="toggle-input"
                @change="updateRule('bookingReminder')"
              >
              <span class="toggle-switch" />
              <span class="toggle-text">{{ rules.bookingReminder.enabled ? '已啟用' : '已停用' }}</span>
            </label>
          </div>
          <div v-if="rules.bookingReminder.enabled" class="rule-settings">
            <div class="setting-item">
              <span class="setting-label">提前通知</span>
              <AppSelect
                v-model="rules.bookingReminder.advanceHours"
                :options="advanceHoursOptions"
                @change="updateRule('bookingReminder')"
              />
            </div>
            <div class="setting-item">
              <span class="setting-label">使用範本</span>
              <AppSelect
                v-model="rules.bookingReminder.templateId"
                :options="reminderTemplateOptions"
                @change="updateRule('bookingReminder')"
              />
            </div>
          </div>
        </div>
      </AppCard>

      <!-- 服務完成感謝函 -->
      <AppCard title="服務完成感謝函">
        <div class="rule-content">
          <div class="rule-description">
            服務完成後自動發送感謝 Email，可包含評價邀請。
          </div>
          <div class="rule-toggle">
            <label class="toggle-label">
              <input
                v-model="rules.serviceComplete.enabled"
                type="checkbox"
                class="toggle-input"
                @change="updateRule('serviceComplete')"
              >
              <span class="toggle-switch" />
              <span class="toggle-text">{{ rules.serviceComplete.enabled ? '已啟用' : '已停用' }}</span>
            </label>
          </div>
          <div v-if="rules.serviceComplete.enabled" class="rule-settings">
            <div class="setting-item">
              <span class="setting-label">發送時間</span>
              <AppSelect
                v-model="rules.serviceComplete.delayHours"
                :options="delayHoursOptions"
                @change="updateRule('serviceComplete')"
              />
            </div>
            <div class="setting-item">
              <span class="setting-label">使用範本</span>
              <AppSelect
                v-model="rules.serviceComplete.templateId"
                :options="thankYouTemplateOptions"
                @change="updateRule('serviceComplete')"
              />
            </div>
          </div>
        </div>
      </AppCard>

      <!-- 生日祝福 -->
      <AppCard title="生日祝福">
        <div class="rule-content">
          <div class="rule-description">
            在顧客生日當天自動發送祝福 Email，可包含專屬優惠。
          </div>
          <div class="rule-toggle">
            <label class="toggle-label">
              <input
                v-model="rules.birthday.enabled"
                type="checkbox"
                class="toggle-input"
                @change="updateRule('birthday')"
              >
              <span class="toggle-switch" />
              <span class="toggle-text">{{ rules.birthday.enabled ? '已啟用' : '已停用' }}</span>
            </label>
          </div>
          <div v-if="rules.birthday.enabled" class="rule-settings">
            <div class="setting-item">
              <span class="setting-label">發送時間</span>
              <AppSelect
                v-model="rules.birthday.sendTime"
                :options="sendTimeOptions"
                @change="updateRule('birthday')"
              />
            </div>
            <div class="setting-item">
              <span class="setting-label">使用範本</span>
              <AppSelect
                v-model="rules.birthday.templateId"
                :options="birthdayTemplateOptions"
                @change="updateRule('birthday')"
              />
            </div>
          </div>
        </div>
      </AppCard>

      <!-- 休眠顧客喚回 -->
      <AppCard title="休眠顧客喚回">
        <div class="rule-content">
          <div class="rule-description">
            自動發送 Email 給長時間未預約的顧客，鼓勵回店消費。
          </div>
          <div class="rule-toggle">
            <label class="toggle-label">
              <input
                v-model="rules.winback.enabled"
                type="checkbox"
                class="toggle-input"
                @change="updateRule('winback')"
              >
              <span class="toggle-switch" />
              <span class="toggle-text">{{ rules.winback.enabled ? '已啟用' : '已停用' }}</span>
            </label>
          </div>
          <div v-if="rules.winback.enabled" class="rule-settings">
            <div class="setting-item">
              <span class="setting-label">休眠天數</span>
              <AppSelect
                v-model="rules.winback.inactiveDays"
                :options="inactiveDaysOptions"
                @change="updateRule('winback')"
              />
            </div>
            <div class="setting-item">
              <span class="setting-label">使用範本</span>
              <AppSelect
                v-model="rules.winback.templateId"
                :options="marketingTemplateOptions"
                @change="updateRule('winback')"
              />
            </div>
          </div>
        </div>
      </AppCard>

      <!-- 預約取消通知 -->
      <AppCard title="預約取消通知">
        <div class="rule-content">
          <div class="rule-description">
            當預約被取消時，自動發送通知 Email 給顧客。
          </div>
          <div class="rule-toggle">
            <label class="toggle-label">
              <input
                v-model="rules.bookingCancel.enabled"
                type="checkbox"
                class="toggle-input"
                @change="updateRule('bookingCancel')"
              >
              <span class="toggle-switch" />
              <span class="toggle-text">{{ rules.bookingCancel.enabled ? '已啟用' : '已停用' }}</span>
            </label>
          </div>
          <div v-if="rules.bookingCancel.enabled" class="rule-settings">
            <div class="setting-item">
              <span class="setting-label">使用範本</span>
              <AppSelect
                v-model="rules.bookingCancel.templateId"
                :options="bookingTemplateOptions"
                @change="updateRule('bookingCancel')"
              />
            </div>
          </div>
        </div>
      </AppCard>
    </div>

    <!-- 發信統計 -->
    <AppCard title="發信統計" class="stats-card">
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-value">{{ stats.totalSent }}</span>
          <span class="stat-label">本月發送</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ formatPercent(stats.openRate) }}</span>
          <span class="stat-label">平均開信率</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ formatPercent(stats.clickRate) }}</span>
          <span class="stat-label">平均點擊率</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ stats.unsubscribed }}</span>
          <span class="stat-label">取消訂閱</span>
        </div>
      </div>
    </AppCard>
  </div>
</template>

<script setup lang="ts">
/**
 * 廠商後台 - 自動發信設定頁面
 * 管理自動 Email 通知規則
 */
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminApi } from '~/composables/useAdminApi'

// 設定使用 admin layout 與認證
definePageMeta({
  layout: 'admin',
  middleware: 'auth'
})

// 路由
const router = useRouter()

// API
const adminApi = useAdminApi()

// 規則介面
interface AutoRule {
  enabled: boolean
  templateId: string
  advanceHours?: number
  delayHours?: number
  sendTime?: string
  inactiveDays?: number
}

// 本地狀態
const loading = ref(false)

// 規則設定
const rules = reactive({
  bookingConfirm: {
    enabled: true,
    templateId: 'default_booking_confirm'
  } as AutoRule,
  bookingReminder: {
    enabled: true,
    templateId: 'default_reminder',
    advanceHours: 24
  } as AutoRule,
  serviceComplete: {
    enabled: false,
    templateId: '',
    delayHours: 2
  } as AutoRule,
  birthday: {
    enabled: true,
    templateId: 'default_birthday',
    sendTime: '09:00'
  } as AutoRule,
  winback: {
    enabled: false,
    templateId: '',
    inactiveDays: 60
  } as AutoRule,
  bookingCancel: {
    enabled: true,
    templateId: ''
  } as AutoRule
})

// 發信統計
const stats = reactive({
  totalSent: 0,
  openRate: 0,
  clickRate: 0,
  unsubscribed: 0
})

// 選項設定
const advanceHoursOptions = [
  { value: 12, label: '12 小時前' },
  { value: 24, label: '1 天前' },
  { value: 48, label: '2 天前' },
  { value: 72, label: '3 天前' }
]

const delayHoursOptions = [
  { value: 1, label: '1 小時後' },
  { value: 2, label: '2 小時後' },
  { value: 24, label: '隔天' }
]

const sendTimeOptions = [
  { value: '08:00', label: '08:00' },
  { value: '09:00', label: '09:00' },
  { value: '10:00', label: '10:00' },
  { value: '12:00', label: '12:00' }
]

const inactiveDaysOptions = [
  { value: 30, label: '30 天未預約' },
  { value: 60, label: '60 天未預約' },
  { value: 90, label: '90 天未預約' }
]

// 範本選項（預設）
const bookingTemplateOptions = [
  { value: '', label: '選擇範本' },
  { value: 'default_booking_confirm', label: '預約確認通知（系統）' }
]

const reminderTemplateOptions = [
  { value: '', label: '選擇範本' },
  { value: 'default_reminder', label: '預約提醒（系統）' }
]

const thankYouTemplateOptions = [
  { value: '', label: '選擇範本' }
]

const birthdayTemplateOptions = [
  { value: '', label: '選擇範本' },
  { value: 'default_birthday', label: '生日祝福（系統）' }
]

const marketingTemplateOptions = [
  { value: '', label: '選擇範本' }
]

// 載入規則
const loadRules = async () => {
  loading.value = true
  try {
    const res = await adminApi.getAutoEmailRules()
    if (res.success && res.data) {
      // 如果 API 有回傳資料，更新規則
      const data = res.data as Record<string, AutoRule>
      if (data.bookingConfirm) Object.assign(rules.bookingConfirm, data.bookingConfirm)
      if (data.bookingReminder) Object.assign(rules.bookingReminder, data.bookingReminder)
      if (data.serviceComplete) Object.assign(rules.serviceComplete, data.serviceComplete)
      if (data.birthday) Object.assign(rules.birthday, data.birthday)
      if (data.winback) Object.assign(rules.winback, data.winback)
      if (data.bookingCancel) Object.assign(rules.bookingCancel, data.bookingCancel)

      // 更新統計
      if ((res.data as { stats?: typeof stats }).stats) {
        Object.assign(stats, (res.data as { stats: typeof stats }).stats)
      }
    }
  } catch (error) {
    console.error('Failed to load auto email rules:', error)
    // 使用預設值，設定模擬統計
    stats.totalSent = 156
    stats.openRate = 0.42
    stats.clickRate = 0.18
    stats.unsubscribed = 3
  } finally {
    loading.value = false
  }
}

// 初始載入
onMounted(() => {
  loadRules()
})

// 更新規則
const updateRule = (ruleName: string) => {
  // 目前 API 尚未實作更新功能
  console.log('Rule updated:', ruleName, (rules as Record<string, AutoRule>)[ruleName])
  // 顯示提示（只在停用時）
  // 實際專案中會呼叫 API 更新
}

// 格式化百分比
const formatPercent = (value: number): string => {
  return `${(value * 100).toFixed(1)}%`
}

// 返回行銷總覽
const goToMarketing = () => {
  router.push('/admin/marketing')
}
</script>

<style scoped>
.admin-automation {
  max-width: 1200px;
  margin: 0 auto;
}

/* 規則網格 */
.rules-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

/* 規則內容 */
.rule-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.rule-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
}

/* Toggle 開關 */
.rule-toggle {
  padding: var(--spacing-sm) 0;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
}

.toggle-input {
  display: none;
}

.toggle-switch {
  position: relative;
  width: 48px;
  height: 24px;
  background: var(--color-border);
  border-radius: 12px;
  transition: background-color 0.2s;
}

.toggle-switch::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: transform 0.2s;
}

.toggle-input:checked + .toggle-switch {
  background: var(--color-primary);
}

.toggle-input:checked + .toggle-switch::after {
  transform: translateX(24px);
}

.toggle-text {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-primary);
}

/* 規則設定 */
.rule-settings {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: var(--color-bg);
  border-radius: var(--radius-md);
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);
}

.setting-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

/* 統計卡片 */
.stats-card {
  margin-top: var(--spacing-lg);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-lg);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-md);
  background: var(--color-bg);
  border-radius: var(--radius-md);
}

.stat-value {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--color-primary);
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* 響應式 */
@media (max-width: 1024px) {
  .rules-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .setting-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
