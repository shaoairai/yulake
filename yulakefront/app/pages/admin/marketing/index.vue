<template>
  <!-- 廠商後台 - Email 行銷管理 -->
  <div class="admin-marketing">
    <!-- 頁面標題 -->
    <AdminPageHeader
      title="Email 行銷"
      description="管理 Email 範本、行銷活動與自動發信規則。"
    >
      <template #actions>
        <AppButton variant="primary" @click="openCreateCampaign">
          ＋ 建立活動
        </AppButton>
      </template>
    </AdminPageHeader>

    <!-- Tab 切換 -->
    <div class="tab-container">
      <button
        :class="['tab-btn', { active: activeTab === 'campaigns' }]"
        @click="activeTab = 'campaigns'"
      >
        行銷活動
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'templates' }]"
        @click="activeTab = 'templates'"
      >
        Email 範本
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'automation' }]"
        @click="activeTab = 'automation'"
      >
        自動發信
      </button>
    </div>

    <!-- 行銷活動列表 -->
    <AppCard v-if="activeTab === 'campaigns'" no-padding>
      <div class="table-wrapper">
        <table class="table">
          <thead>
            <tr>
              <th>活動名稱</th>
              <th>範本</th>
              <th>收件人數</th>
              <th>排程時間</th>
              <th>狀態</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="campaign in campaigns" :key="campaign.id">
              <td>
                <span class="campaign-name">{{ campaign.name }}</span>
              </td>
              <td>{{ campaign.template_name || '-' }}</td>
              <td>{{ campaign.total_recipients || 0 }} 人</td>
              <td>{{ formatDate(campaign.scheduled_at) }}</td>
              <td>
                <AppBadge :variant="getCampaignStatusVariant(campaign.status)">
                  {{ getCampaignStatusLabel(campaign.status) }}
                </AppBadge>
              </td>
              <td>
                <div class="campaign-actions">
                  <AppButton
                    v-if="campaign.status === 'draft'"
                    variant="ghost"
                    size="sm"
                    @click="editCampaign(campaign)"
                  >
                    編輯
                  </AppButton>
                  <AppButton
                    v-if="campaign.status === 'draft' || campaign.status === 'scheduled'"
                    variant="ghost"
                    size="sm"
                    @click="sendCampaign(campaign)"
                  >
                    發送
                  </AppButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="campaigns.length === 0" class="admin-empty-state">
        <span class="empty-icon">📧</span>
        <p class="empty-title">尚無行銷活動</p>
        <p class="empty-description">點擊「建立活動」開始您的第一個 Email 行銷</p>
      </div>
    </AppCard>

    <!-- Email 範本列表 -->
    <AppCard v-if="activeTab === 'templates'" no-padding>
      <template #header>
        <div class="card-header-actions">
          <AppButton variant="outline" size="sm" @click="openAddTemplate">
            ＋ 新增範本
          </AppButton>
        </div>
      </template>

      <div class="table-wrapper">
        <table class="table">
          <thead>
            <tr>
              <th>範本名稱</th>
              <th>類型</th>
              <th>主旨</th>
              <th>狀態</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="template in templates" :key="template.id">
              <td>
                <span class="template-name">{{ template.name }}</span>
              </td>
              <td>
                <AppBadge variant="info">
                  {{ getTemplateTypeLabel(template.type) }}
                </AppBadge>
              </td>
              <td class="template-subject">{{ template.subject }}</td>
              <td>
                <AppBadge :variant="template.is_active ? 'success' : 'default'">
                  {{ template.is_active ? '啟用' : '停用' }}
                </AppBadge>
              </td>
              <td>
                <div class="template-actions">
                  <AppButton variant="ghost" size="sm" @click="editTemplate(template)">
                    編輯
                  </AppButton>
                  <AppButton variant="ghost" size="sm" @click="previewTemplate(template)">
                    預覽
                  </AppButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="templates.length === 0" class="admin-empty-state">
        <span class="empty-icon">📝</span>
        <p class="empty-title">尚無 Email 範本</p>
        <p class="empty-description">點擊「新增範本」建立您的第一個範本</p>
      </div>
    </AppCard>

    <!-- 自動發信規則 -->
    <AppCard v-if="activeTab === 'automation'" title="自動發信規則">
      <div class="automation-list">
        <div v-for="rule in autoRules" :key="rule.type" class="automation-item">
          <div class="automation-info">
            <div class="automation-icon">{{ getAutoRuleIcon(rule.type) }}</div>
            <div class="automation-content">
              <h4 class="automation-title">{{ getAutoRuleTitle(rule.type) }}</h4>
              <p class="automation-desc">{{ getAutoRuleDesc(rule.type) }}</p>
            </div>
          </div>
          <div class="automation-actions">
            <label class="switch">
              <input
                type="checkbox"
                :checked="rule.is_active"
                @change="toggleAutoRule(rule)"
              >
              <span class="slider"></span>
            </label>
            <AppButton variant="ghost" size="sm" @click="configAutoRule(rule)">
              設定
            </AppButton>
          </div>
        </div>
      </div>
    </AppCard>

    <!-- 新增/編輯範本 Modal -->
    <AppModal
      v-model="showTemplateModal"
      :title="isEditingTemplate ? '編輯範本' : '新增範本'"
      size="lg"
    >
      <form class="template-form" @submit.prevent="handleTemplateSubmit">
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">
              範本名稱 <span class="required">*</span>
            </label>
            <AppInput
              v-model="templateForm.name"
              placeholder="例如：預約確認通知"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">範本類型</label>
            <AppSelect v-model="templateForm.type">
              <option value="booking_confirm">預約確認</option>
              <option value="booking_reminder">預約提醒</option>
              <option value="birthday">生日祝福</option>
              <option value="revisit">回訪提醒</option>
              <option value="promotion">促銷活動</option>
            </AppSelect>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">
            信件主旨 <span class="required">*</span>
          </label>
          <AppInput
            v-model="templateForm.subject"
            placeholder="例如：【{{salon_name}}】您的預約已確認"
            required
          />
          <p class="form-hint">可使用變數：{{salon_name}}, {{customer_name}}, {{service_name}}, {{booking_date}}, {{start_time}}</p>
        </div>

        <div class="form-group">
          <label class="form-label">
            信件內容 <span class="required">*</span>
          </label>
          <textarea
            v-model="templateForm.body"
            class="form-textarea"
            rows="10"
            placeholder="輸入 Email 內容..."
            required
          ></textarea>
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input
              v-model="templateForm.is_active"
              type="checkbox"
              class="checkbox-input"
            >
            <span>啟用此範本</span>
          </label>
        </div>
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="closeTemplateModal">
          取消
        </AppButton>
        <AppButton variant="primary" :loading="saving" @click="handleTemplateSubmit">
          {{ isEditingTemplate ? '儲存變更' : '新增範本' }}
        </AppButton>
      </template>
    </AppModal>

    <!-- 建立行銷活動 Modal -->
    <AppModal
      v-model="showCampaignModal"
      title="建立行銷活動"
      size="md"
    >
      <form class="campaign-form" @submit.prevent="handleCampaignSubmit">
        <div class="form-group">
          <label class="form-label">
            活動名稱 <span class="required">*</span>
          </label>
          <AppInput
            v-model="campaignForm.name"
            placeholder="例如：夏季優惠活動"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label">選擇範本</label>
          <AppSelect v-model="campaignForm.template_id">
            <option value="">請選擇範本</option>
            <option
              v-for="t in templates.filter(t => t.is_active)"
              :key="t.id"
              :value="t.id"
            >
              {{ t.name }}
            </option>
          </AppSelect>
        </div>

        <div class="form-group">
          <label class="form-label">目標客群</label>
          <AppSelect v-model="campaignForm.target_type">
            <option value="all">全部顧客</option>
            <option value="tier">指定等級</option>
            <option value="inactive">沉睡顧客</option>
            <option value="birthday_month">本月壽星</option>
          </AppSelect>
        </div>

        <div class="form-group">
          <label class="form-label">排程發送時間</label>
          <AppInput
            v-model="campaignForm.scheduled_at"
            type="datetime-local"
          />
          <p class="form-hint">留空則儲存為草稿</p>
        </div>
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="closeCampaignModal">
          取消
        </AppButton>
        <AppButton variant="primary" :loading="saving" @click="handleCampaignSubmit">
          建立活動
        </AppButton>
      </template>
    </AppModal>
  </div>
</template>

<script setup lang="ts">
/**
 * 廠商後台 - Email 行銷管理頁面
 * 管理 Email 範本、行銷活動與自動發信規則
 */
import { ref, reactive, onMounted } from 'vue'
import { useAdminApi } from '~/composables/useAdminApi'

// 設定使用 admin layout 與認證
definePageMeta({
  layout: 'admin',
  middleware: 'auth'
})

const adminApi = useAdminApi()

// Tab 狀態
const activeTab = ref<'campaigns' | 'templates' | 'automation'>('campaigns')

// 載入狀態
const loading = ref(false)
const saving = ref(false)

// 資料
interface EmailTemplate {
  id: string
  name: string
  type: string
  subject: string
  body: string
  is_active: boolean
}

interface EmailCampaign {
  id: string
  name: string
  template_id?: string
  template_name?: string
  target_type: string
  scheduled_at?: string
  status: string
  total_recipients?: number
}

interface AutoEmailRule {
  type: string
  template_id?: string
  config: string
  is_active: boolean
}

const templates = ref<EmailTemplate[]>([])
const campaigns = ref<EmailCampaign[]>([])
const autoRules = ref<AutoEmailRule[]>([])

// Modal 狀態
const showTemplateModal = ref(false)
const showCampaignModal = ref(false)
const isEditingTemplate = ref(false)
const editingTemplateId = ref<string | null>(null)

// 範本表單
const templateForm = reactive({
  name: '',
  type: 'promotion',
  subject: '',
  body: '',
  is_active: true
})

// 活動表單
const campaignForm = reactive({
  name: '',
  template_id: '',
  target_type: 'all',
  scheduled_at: ''
})

// 載入資料
const loadData = async () => {
  loading.value = true
  try {
    const [templatesRes, campaignsRes, rulesRes] = await Promise.all([
      adminApi.getEmailTemplates(),
      adminApi.getEmailCampaigns(),
      adminApi.getAutoEmailRules()
    ])

    if (templatesRes.success) {
      templates.value = templatesRes.data
    }

    if (campaignsRes.success) {
      campaigns.value = campaignsRes.data
    }

    if (rulesRes.success) {
      autoRules.value = rulesRes.data
    }
  } catch (error) {
    console.error('Failed to load marketing data:', error)
  } finally {
    loading.value = false
  }
}

// 格式化日期
const formatDate = (date?: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-TW')
}

// 取得活動狀態標籤
const getCampaignStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    draft: '草稿',
    scheduled: '已排程',
    sending: '發送中',
    sent: '已發送',
    cancelled: '已取消'
  }
  return labels[status] || status
}

// 取得活動狀態樣式
const getCampaignStatusVariant = (status: string) => {
  const variants: Record<string, string> = {
    draft: 'default',
    scheduled: 'warning',
    sending: 'info',
    sent: 'success',
    cancelled: 'error'
  }
  return variants[status] || 'default'
}

// 取得範本類型標籤
const getTemplateTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    booking_confirm: '預約確認',
    booking_reminder: '預約提醒',
    birthday: '生日祝福',
    revisit: '回訪提醒',
    promotion: '促銷活動'
  }
  return labels[type] || type
}

// 取得自動發信規則圖示
const getAutoRuleIcon = (type: string) => {
  const icons: Record<string, string> = {
    booking_confirm: '✅',
    booking_reminder: '⏰',
    birthday: '🎂',
    revisit: '👋',
    no_show_warning: '⚠️'
  }
  return icons[type] || '📧'
}

// 取得自動發信規則標題
const getAutoRuleTitle = (type: string) => {
  const titles: Record<string, string> = {
    booking_confirm: '預約確認通知',
    booking_reminder: '預約提醒',
    birthday: '生日祝福',
    revisit: '回訪提醒',
    no_show_warning: '爽約警告'
  }
  return titles[type] || type
}

// 取得自動發信規則說明
const getAutoRuleDesc = (type: string) => {
  const descs: Record<string, string> = {
    booking_confirm: '顧客預約成功後自動發送確認信',
    booking_reminder: '預約前自動發送提醒信（預設 24 小時前）',
    birthday: '顧客生日當月自動發送祝福信',
    revisit: '顧客超過指定天數未來店時發送邀約信',
    no_show_warning: '顧客爽約時發送提醒信'
  }
  return descs[type] || ''
}

// 開啟新增範本 Modal
const openAddTemplate = () => {
  templateForm.name = ''
  templateForm.type = 'promotion'
  templateForm.subject = ''
  templateForm.body = ''
  templateForm.is_active = true
  editingTemplateId.value = null
  isEditingTemplate.value = false
  showTemplateModal.value = true
}

// 編輯範本
const editTemplate = (template: EmailTemplate) => {
  templateForm.name = template.name
  templateForm.type = template.type
  templateForm.subject = template.subject
  templateForm.body = template.body
  templateForm.is_active = template.is_active
  editingTemplateId.value = template.id
  isEditingTemplate.value = true
  showTemplateModal.value = true
}

// 關閉範本 Modal
const closeTemplateModal = () => {
  showTemplateModal.value = false
}

// 預覽範本
const previewTemplate = (template: EmailTemplate) => {
  alert(`主旨：${template.subject}\n\n內容：\n${template.body}`)
}

// 提交範本表單
const handleTemplateSubmit = async () => {
  if (!templateForm.name.trim() || !templateForm.subject.trim() || !templateForm.body.trim()) {
    alert('請填寫所有必填欄位')
    return
  }

  saving.value = true
  try {
    // API 呼叫（這裡簡化處理）
    alert(isEditingTemplate.value ? '範本已更新' : '範本已新增')
    closeTemplateModal()
    await loadData()
  } catch (error) {
    console.error('Failed to save template:', error)
    alert('儲存失敗')
  } finally {
    saving.value = false
  }
}

// 開啟建立活動 Modal
const openCreateCampaign = () => {
  campaignForm.name = ''
  campaignForm.template_id = ''
  campaignForm.target_type = 'all'
  campaignForm.scheduled_at = ''
  showCampaignModal.value = true
}

// 關閉活動 Modal
const closeCampaignModal = () => {
  showCampaignModal.value = false
}

// 編輯活動
const editCampaign = (campaign: EmailCampaign) => {
  campaignForm.name = campaign.name
  campaignForm.template_id = campaign.template_id || ''
  campaignForm.target_type = campaign.target_type
  campaignForm.scheduled_at = campaign.scheduled_at || ''
  showCampaignModal.value = true
}

// 發送活動
const sendCampaign = async (campaign: EmailCampaign) => {
  if (!confirm(`確定要發送活動「${campaign.name}」嗎？`)) return
  alert('活動已開始發送')
  await loadData()
}

// 提交活動表單
const handleCampaignSubmit = async () => {
  if (!campaignForm.name.trim()) {
    alert('請輸入活動名稱')
    return
  }

  saving.value = true
  try {
    alert('活動已建立')
    closeCampaignModal()
    await loadData()
  } catch (error) {
    console.error('Failed to save campaign:', error)
    alert('儲存失敗')
  } finally {
    saving.value = false
  }
}

// 切換自動發信規則
const toggleAutoRule = async (rule: AutoEmailRule) => {
  const action = rule.is_active ? '停用' : '啟用'
  alert(`已${action}「${getAutoRuleTitle(rule.type)}」`)
  rule.is_active = !rule.is_active
}

// 設定自動發信規則
const configAutoRule = (rule: AutoEmailRule) => {
  alert(`設定「${getAutoRuleTitle(rule.type)}」功能開發中`)
}

// 初始載入
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.admin-marketing {
  max-width: 1200px;
  margin: 0 auto;
}

/* Tab 容器 */
.tab-container {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
  padding-bottom: var(--spacing-sm);
}

.tab-btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  background: transparent;
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.tab-btn:hover {
  background-color: var(--color-bg-hover);
}

.tab-btn.active {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
}

/* 卡片標題操作 */
.card-header-actions {
  display: flex;
  justify-content: flex-end;
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
}

/* 活動名稱 */
.campaign-name,
.template-name {
  font-weight: 500;
  color: var(--color-text-primary);
}

.template-subject {
  max-width: 250px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--color-text-secondary);
}

.campaign-actions,
.template-actions {
  display: flex;
  gap: var(--spacing-xs);
}

/* 自動發信列表 */
.automation-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.automation-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
}

.automation-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.automation-icon {
  font-size: 24px;
}

.automation-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.automation-title {
  margin: 0;
  font-size: var(--font-size-base);
  font-weight: 500;
  color: var(--color-text-primary);
}

.automation-desc {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.automation-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

/* Switch 開關 */
.switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 26px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--color-border);
  transition: 0.3s;
  border-radius: 26px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: var(--color-primary);
}

input:checked + .slider:before {
  transform: translateX(22px);
}

/* 表單樣式 */
.template-form,
.campaign-form {
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

.form-label .required {
  color: var(--color-error);
}

.form-hint {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  margin: 0;
}

.form-textarea {
  width: 100%;
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-family: inherit;
  resize: vertical;
}

.form-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

/* Checkbox 樣式 */
.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.checkbox-input {
  width: 18px;
  height: 18px;
  accent-color: var(--color-primary);
}

/* 響應式 */
@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .automation-item {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }

  .automation-actions {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
