<template>
  <!-- 廠商後台 - Email 範本管理 -->
  <div class="admin-templates">
    <!-- 頁面標題 -->
    <AdminPageHeader
      title="Email 範本"
      description="管理 Email 範本，用於行銷活動與自動發信"
    >
      <template #actions>
        <AppButton variant="outline" size="sm" @click="goToMarketing">
          返回行銷總覽
        </AppButton>
        <AppButton variant="primary" size="sm" @click="openCreateModal">
          ＋ 新增範本
        </AppButton>
      </template>
    </AdminPageHeader>

    <!-- 篩選列 -->
    <div class="filter-bar">
      <div class="filter-group">
        <label>類型</label>
        <AppSelect
          v-model="filterType"
          :options="typeOptions"
          placeholder="全部類型"
        />
      </div>
      <AppButton variant="outline" size="sm" @click="loadTemplates">
        套用篩選
      </AppButton>
    </div>

    <!-- 範本列表 -->
    <AppCard>
      <div v-if="loading" class="loading-state">
        載入中...
      </div>
      <div v-else-if="templates.length === 0" class="empty-state">
        <p>尚無 Email 範本</p>
        <AppButton variant="primary" size="sm" @click="openCreateModal">
          新增第一個範本
        </AppButton>
      </div>
      <div v-else class="templates-grid">
        <div
          v-for="template in filteredTemplates"
          :key="template.id"
          class="template-card"
        >
          <div class="template-header">
            <h3 class="template-name">{{ template.name }}</h3>
            <AppBadge :variant="getTypeVariant(template.type)">
              {{ getTypeLabel(template.type) }}
            </AppBadge>
          </div>
          <div class="template-subject">
            主旨：{{ template.subject || '（未設定）' }}
          </div>
          <div v-if="template.description" class="template-description">
            {{ template.description }}
          </div>
          <div class="template-preview">
            <div class="preview-content" v-html="truncateContent(template.content)" />
          </div>
          <div class="template-meta">
            <span>更新於：{{ formatDate(template.updated_at || template.created_at) }}</span>
          </div>
          <div class="template-actions">
            <AppButton variant="outline" size="sm" @click="previewTemplate(template)">
              預覽
            </AppButton>
            <AppButton variant="ghost" size="sm" @click="editTemplate(template)">
              編輯
            </AppButton>
            <AppButton
              v-if="!template.is_system"
              variant="ghost"
              size="sm"
              @click="deleteTemplate(template.id)"
            >
              刪除
            </AppButton>
          </div>
        </div>
      </div>
    </AppCard>

    <!-- 新增/編輯 Modal -->
    <AppModal
      v-model="showModal"
      :title="editingTemplate ? '編輯範本' : '新增範本'"
      size="large"
    >
      <form class="template-form" @submit.prevent="saveTemplate">
        <div class="form-group">
          <label class="form-label">範本名稱 <span class="required">*</span></label>
          <AppInput
            v-model="formData.name"
            placeholder="輸入範本名稱"
            required
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">類型 <span class="required">*</span></label>
            <AppSelect
              v-model="formData.type"
              :options="templateTypeOptions"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">Email 主旨</label>
            <AppInput
              v-model="formData.subject"
              placeholder="輸入預設主旨"
            />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">說明</label>
          <AppInput
            v-model="formData.description"
            placeholder="輸入範本說明（選填）"
          />
        </div>

        <div class="form-group">
          <label class="form-label">範本內容</label>
          <div class="content-hint">
            支援 HTML 格式。可使用變數：{customer_name}、{salon_name}、{booking_date}、{service_name}
          </div>
          <textarea
            v-model="formData.content"
            class="form-textarea"
            rows="12"
            placeholder="輸入 Email 內容（支援 HTML）"
          />
        </div>
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="closeModal">
          取消
        </AppButton>
        <AppButton variant="primary" @click="saveTemplate">
          {{ editingTemplate ? '更新' : '新增' }}
        </AppButton>
      </template>
    </AppModal>

    <!-- 預覽 Modal -->
    <AppModal
      v-model="showPreviewModal"
      title="範本預覽"
      size="large"
    >
      <div v-if="previewingTemplate" class="template-preview-modal">
        <div class="preview-header">
          <strong>主旨：</strong> {{ previewingTemplate.subject || '（未設定）' }}
        </div>
        <div class="preview-body" v-html="previewingTemplate.content" />
      </div>

      <template #footer>
        <AppButton variant="ghost" @click="showPreviewModal = false">
          關閉
        </AppButton>
      </template>
    </AppModal>
  </div>
</template>

<script setup lang="ts">
/**
 * 廠商後台 - Email 範本管理頁面
 * 管理用於行銷活動與自動發信的 Email 範本
 */
import { ref, reactive, computed, onMounted } from 'vue'
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

// 範本介面
interface EmailTemplate {
  id: string
  name: string
  type: string
  subject?: string
  description?: string
  content: string
  is_system?: boolean
  created_at: string
  updated_at?: string
}

// 本地狀態
const loading = ref(false)
const templates = ref<EmailTemplate[]>([])
const showModal = ref(false)
const showPreviewModal = ref(false)
const editingTemplate = ref<EmailTemplate | null>(null)
const previewingTemplate = ref<EmailTemplate | null>(null)

// 篩選
const filterType = ref('')

// 類型選項
const typeOptions = [
  { value: '', label: '全部類型' },
  { value: 'marketing', label: '行銷推廣' },
  { value: 'booking', label: '預約通知' },
  { value: 'reminder', label: '提醒通知' },
  { value: 'thank_you', label: '感謝函' },
  { value: 'birthday', label: '生日祝福' },
  { value: 'custom', label: '自訂' }
]

// 範本類型選項（新增/編輯用）
const templateTypeOptions = [
  { value: 'marketing', label: '行銷推廣' },
  { value: 'booking', label: '預約通知' },
  { value: 'reminder', label: '提醒通知' },
  { value: 'thank_you', label: '感謝函' },
  { value: 'birthday', label: '生日祝福' },
  { value: 'custom', label: '自訂' }
]

// 類型標籤
const typeLabels: Record<string, string> = {
  marketing: '行銷推廣',
  booking: '預約通知',
  reminder: '提醒通知',
  thank_you: '感謝函',
  birthday: '生日祝福',
  custom: '自訂'
}

// 類型樣式
const typeVariants: Record<string, 'default' | 'primary' | 'success' | 'warning' | 'error'> = {
  marketing: 'primary',
  booking: 'success',
  reminder: 'warning',
  thank_you: 'success',
  birthday: 'primary',
  custom: 'default'
}

// 表單資料
const formData = reactive({
  name: '',
  type: 'custom',
  subject: '',
  description: '',
  content: ''
})

// 載入範本
const loadTemplates = async () => {
  loading.value = true
  try {
    const res = await adminApi.getEmailTemplates(filterType.value || undefined)
    if (res.success && res.data) {
      templates.value = res.data as EmailTemplate[]
    }
  } catch (error) {
    console.error('Failed to load templates:', error)
    // 使用預設範本
    templates.value = getDefaultTemplates()
  } finally {
    loading.value = false
  }
}

// 預設範本（如果 API 無資料）
const getDefaultTemplates = (): EmailTemplate[] => [
  {
    id: 'default_booking_confirm',
    name: '預約確認通知',
    type: 'booking',
    subject: '【{salon_name}】您的預約已確認',
    description: '預約確認時自動發送',
    content: `<h2>親愛的 {customer_name}，您好！</h2>
<p>感謝您的預約，以下是您的預約資訊：</p>
<ul>
  <li>日期：{booking_date}</li>
  <li>服務：{service_name}</li>
</ul>
<p>如需更改或取消預約，請提前聯繫我們。</p>
<p>期待您的光臨！</p>
<p>{salon_name} 敬上</p>`,
    is_system: true,
    created_at: new Date().toISOString()
  },
  {
    id: 'default_reminder',
    name: '預約提醒',
    type: 'reminder',
    subject: '【{salon_name}】明天的預約提醒',
    description: '預約前一天自動發送',
    content: `<h2>親愛的 {customer_name}，您好！</h2>
<p>溫馨提醒您，明天有一個預約：</p>
<ul>
  <li>日期：{booking_date}</li>
  <li>服務：{service_name}</li>
</ul>
<p>請準時到達，如有任何問題請聯繫我們。</p>
<p>{salon_name} 敬上</p>`,
    is_system: true,
    created_at: new Date().toISOString()
  },
  {
    id: 'default_birthday',
    name: '生日祝福',
    type: 'birthday',
    subject: '【{salon_name}】祝您生日快樂！',
    description: '顧客生日當天自動發送',
    content: `<h2>親愛的 {customer_name}，生日快樂！</h2>
<p>感謝您一直以來的支持與信任。</p>
<p>在這特別的日子，我們為您準備了專屬優惠，歡迎來店體驗！</p>
<p>{salon_name} 全體同仁 敬祝</p>`,
    is_system: true,
    created_at: new Date().toISOString()
  }
]

// 初始載入
onMounted(() => {
  loadTemplates()
})

// 篩選後的範本
const filteredTemplates = computed(() => {
  if (!filterType.value) {
    return templates.value
  }
  return templates.value.filter(t => t.type === filterType.value)
})

// 取得類型標籤
const getTypeLabel = (type: string): string => {
  return typeLabels[type] || type
}

// 取得類型樣式
const getTypeVariant = (type: string) => {
  return typeVariants[type] || 'default'
}

// 格式化日期
const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 截斷內容
const truncateContent = (content: string): string => {
  // 移除 HTML 標籤，只保留文字
  const text = content.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim()
  if (text.length > 100) {
    return text.substring(0, 100) + '...'
  }
  return text
}

// 重置表單
const resetForm = () => {
  formData.name = ''
  formData.type = 'custom'
  formData.subject = ''
  formData.description = ''
  formData.content = ''
}

// 開啟新增 Modal
const openCreateModal = () => {
  editingTemplate.value = null
  resetForm()
  showModal.value = true
}

// 編輯範本
const editTemplate = (template: EmailTemplate) => {
  if (template.is_system) {
    alert('系統範本無法編輯。您可以複製一份新範本進行修改。')
    return
  }
  editingTemplate.value = template
  formData.name = template.name
  formData.type = template.type
  formData.subject = template.subject || ''
  formData.description = template.description || ''
  formData.content = template.content
  showModal.value = true
}

// 預覽範本
const previewTemplate = (template: EmailTemplate) => {
  previewingTemplate.value = template
  showPreviewModal.value = true
}

// 關閉 Modal
const closeModal = () => {
  showModal.value = false
  editingTemplate.value = null
  resetForm()
}

// 儲存範本
const saveTemplate = async () => {
  if (!formData.name || !formData.type) {
    alert('請填寫範本名稱和類型')
    return
  }

  // 目前 API 尚未實作 create/update，顯示提示
  alert('範本管理功能將於後續版本完整實作。\n\n目前可檢視預設範本。')
  closeModal()
}

// 刪除範本
const deleteTemplate = (templateId: string) => {
  if (confirm('確定要刪除此範本嗎？')) {
    alert('刪除功能將於後續版本實作。')
  }
}

// 返回行銷總覽
const goToMarketing = () => {
  router.push('/admin/marketing')
}
</script>

<style scoped>
.admin-templates {
  max-width: 1400px;
  margin: 0 auto;
}

/* 篩選列 */
.filter-bar {
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

/* 載入與空狀態 */
.loading-state,
.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--color-text-secondary);
}

.empty-state p {
  margin-bottom: var(--spacing-md);
}

/* 範本網格 */
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-lg);
}

.template-card {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  padding: var(--spacing-lg);
  background: var(--color-bg);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
}

.template-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-sm);
}

.template-name {
  font-size: var(--font-size-md);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.template-subject {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.template-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.template-preview {
  flex: 1;
  padding: var(--spacing-sm);
  background: var(--color-bg-card);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border-light);
}

.preview-content {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.template-meta {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.template-actions {
  display: flex;
  gap: var(--spacing-xs);
  margin-top: var(--spacing-sm);
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--color-border-light);
}

/* 表單 */
.template-form {
  display: flex;
  flex-direction: column;
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.content-hint {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  margin-bottom: var(--spacing-xs);
}

.form-textarea {
  width: 100%;
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-family: monospace;
  resize: vertical;
}

.form-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

/* 預覽 Modal */
.template-preview-modal {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.preview-header {
  padding: var(--spacing-sm);
  background: var(--color-bg);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
}

.preview-body {
  padding: var(--spacing-lg);
  background: white;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
}

/* 響應式 */
@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group {
    min-width: auto;
  }

  .templates-grid {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
