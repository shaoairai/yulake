<template>
  <!-- 廠商後台 - 行銷活動管理 -->
  <div class="admin-campaigns">
    <!-- 頁面標題 -->
    <AdminPageHeader
      title="行銷活動"
      description="管理 Email 行銷活動，發送優惠通知與活動訊息"
    >
      <template #actions>
        <AppButton variant="outline" size="sm" @click="goToMarketing">
          返回行銷總覽
        </AppButton>
        <AppButton variant="primary" size="sm" @click="openCreateModal">
          ＋ 建立活動
        </AppButton>
      </template>
    </AdminPageHeader>

    <!-- 篩選列 -->
    <div class="filter-bar">
      <div class="filter-group">
        <label>狀態</label>
        <AppSelect
          v-model="filterStatus"
          :options="statusOptions"
          placeholder="全部狀態"
        />
      </div>
      <AppButton variant="outline" size="sm" @click="loadCampaigns">
        套用篩選
      </AppButton>
    </div>

    <!-- 活動列表 -->
    <AppCard>
      <div v-if="loading" class="loading-state">
        載入中...
      </div>
      <div v-else-if="campaigns.length === 0" class="empty-state">
        <p>尚無行銷活動</p>
        <AppButton variant="primary" size="sm" @click="openCreateModal">
          建立第一個活動
        </AppButton>
      </div>
      <div v-else class="campaigns-list">
        <div
          v-for="campaign in campaigns"
          :key="campaign.id"
          class="campaign-item"
        >
          <div class="campaign-info">
            <div class="campaign-header">
              <h3 class="campaign-name">{{ campaign.name }}</h3>
              <AppBadge :variant="getStatusVariant(campaign.status)">
                {{ getStatusLabel(campaign.status) }}
              </AppBadge>
            </div>
            <div class="campaign-meta">
              <span class="campaign-subject">主旨：{{ campaign.subject }}</span>
            </div>
            <div class="campaign-stats">
              <div class="stat-item">
                <span class="stat-label">發送數</span>
                <span class="stat-value">{{ campaign.sent_count || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">開信率</span>
                <span class="stat-value">{{ formatPercent(campaign.open_rate) }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">點擊率</span>
                <span class="stat-value">{{ formatPercent(campaign.click_rate) }}</span>
              </div>
            </div>
            <div class="campaign-dates">
              <span v-if="campaign.scheduled_at">
                預定發送：{{ formatDateTime(campaign.scheduled_at) }}
              </span>
              <span v-if="campaign.sent_at">
                已發送：{{ formatDateTime(campaign.sent_at) }}
              </span>
              <span>建立於：{{ formatDateTime(campaign.created_at) }}</span>
            </div>
          </div>
          <div class="campaign-actions">
            <AppButton
              v-if="campaign.status === 'draft'"
              variant="primary"
              size="sm"
              @click="sendCampaign(campaign)"
            >
              發送
            </AppButton>
            <AppButton
              v-if="campaign.status === 'draft'"
              variant="ghost"
              size="sm"
              @click="editCampaign(campaign)"
            >
              編輯
            </AppButton>
            <AppButton
              variant="ghost"
              size="sm"
              @click="viewCampaign(campaign)"
            >
              詳情
            </AppButton>
            <AppButton
              v-if="campaign.status === 'draft'"
              variant="ghost"
              size="sm"
              @click="deleteCampaign(campaign.id)"
            >
              刪除
            </AppButton>
          </div>
        </div>
      </div>

      <!-- 分頁 -->
      <div v-if="totalPages > 1" class="pagination">
        <AppButton
          variant="ghost"
          size="sm"
          :disabled="currentPage <= 1"
          @click="goToPage(currentPage - 1)"
        >
          上一頁
        </AppButton>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <AppButton
          variant="ghost"
          size="sm"
          :disabled="currentPage >= totalPages"
          @click="goToPage(currentPage + 1)"
        >
          下一頁
        </AppButton>
      </div>
    </AppCard>

    <!-- 建立/編輯 Modal -->
    <AppModal
      v-model="showModal"
      :title="editingCampaign ? '編輯活動' : '建立活動'"
      size="large"
    >
      <form class="campaign-form" @submit.prevent="saveCampaign">
        <div class="form-group">
          <label class="form-label">活動名稱 <span class="required">*</span></label>
          <AppInput
            v-model="formData.name"
            placeholder="輸入活動名稱（內部識別用）"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label">Email 主旨 <span class="required">*</span></label>
          <AppInput
            v-model="formData.subject"
            placeholder="輸入 Email 主旨"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label">選擇範本</label>
          <AppSelect
            v-model="formData.template_id"
            :options="templateOptions"
            placeholder="選擇 Email 範本"
          />
        </div>

        <div class="form-group">
          <label class="form-label">目標客群</label>
          <AppSelect
            v-model="formData.target_audience"
            :options="audienceOptions"
            placeholder="選擇目標客群"
          />
        </div>

        <div class="form-group">
          <label class="form-label">排程發送</label>
          <AppInput
            v-model="formData.scheduled_at"
            type="datetime-local"
            placeholder="留空則手動發送"
          />
        </div>

        <div class="form-group">
          <label class="form-label">Email 內容</label>
          <textarea
            v-model="formData.content"
            class="form-textarea"
            rows="8"
            placeholder="輸入 Email 內容（支援 HTML）"
          />
        </div>
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="closeModal">
          取消
        </AppButton>
        <AppButton variant="primary" @click="saveCampaign">
          {{ editingCampaign ? '更新' : '建立' }}
        </AppButton>
      </template>
    </AppModal>

    <!-- 詳情 Modal -->
    <AppModal
      v-model="showDetailModal"
      title="活動詳情"
      size="large"
    >
      <div v-if="viewingCampaign" class="campaign-detail">
        <div class="detail-row">
          <span class="detail-label">活動名稱</span>
          <span class="detail-value">{{ viewingCampaign.name }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Email 主旨</span>
          <span class="detail-value">{{ viewingCampaign.subject }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">狀態</span>
          <span class="detail-value">
            <AppBadge :variant="getStatusVariant(viewingCampaign.status)">
              {{ getStatusLabel(viewingCampaign.status) }}
            </AppBadge>
          </span>
        </div>
        <div class="detail-row">
          <span class="detail-label">發送數</span>
          <span class="detail-value">{{ viewingCampaign.sent_count || 0 }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">開信率</span>
          <span class="detail-value">{{ formatPercent(viewingCampaign.open_rate) }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">點擊率</span>
          <span class="detail-value">{{ formatPercent(viewingCampaign.click_rate) }}</span>
        </div>
        <div v-if="viewingCampaign.content" class="detail-row detail-row--full">
          <span class="detail-label">內容預覽</span>
          <div class="detail-content" v-html="viewingCampaign.content" />
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
 * 廠商後台 - 行銷活動管理頁面
 * 管理 Email 行銷活動
 */
import { ref, reactive, onMounted, computed } from 'vue'
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

// 活動介面
interface Campaign {
  id: string
  name: string
  subject: string
  content?: string
  status: 'draft' | 'scheduled' | 'sending' | 'sent' | 'cancelled'
  template_id?: string
  target_audience?: string
  sent_count?: number
  open_rate?: number
  click_rate?: number
  scheduled_at?: string
  sent_at?: string
  created_at: string
}

// 範本介面
interface EmailTemplate {
  id: string
  name: string
  type: string
}

// 本地狀態
const loading = ref(false)
const campaigns = ref<Campaign[]>([])
const templates = ref<EmailTemplate[]>([])
const showModal = ref(false)
const showDetailModal = ref(false)
const editingCampaign = ref<Campaign | null>(null)
const viewingCampaign = ref<Campaign | null>(null)

// 分頁
const currentPage = ref(1)
const totalPages = ref(1)
const perPage = 10

// 篩選
const filterStatus = ref('')

// 狀態選項
const statusOptions = [
  { value: '', label: '全部狀態' },
  { value: 'draft', label: '草稿' },
  { value: 'scheduled', label: '已排程' },
  { value: 'sending', label: '發送中' },
  { value: 'sent', label: '已發送' },
  { value: 'cancelled', label: '已取消' }
]

// 目標客群選項
const audienceOptions = [
  { value: 'all', label: '全部顧客' },
  { value: 'active', label: '活躍顧客（30天內有預約）' },
  { value: 'inactive', label: '休眠顧客（超過60天未預約）' },
  { value: 'vip', label: 'VIP 會員' },
  { value: 'birthday', label: '本月壽星' }
]

// 範本選項
const templateOptions = computed(() => [
  { value: '', label: '不使用範本' },
  ...templates.value.map(t => ({ value: t.id, label: t.name }))
])

// 表單資料
const formData = reactive({
  name: '',
  subject: '',
  content: '',
  template_id: '',
  target_audience: 'all',
  scheduled_at: ''
})

// 狀態標籤
const statusLabels: Record<string, string> = {
  draft: '草稿',
  scheduled: '已排程',
  sending: '發送中',
  sent: '已發送',
  cancelled: '已取消'
}

// 狀態樣式
const statusVariants: Record<string, 'default' | 'primary' | 'success' | 'warning' | 'error'> = {
  draft: 'default',
  scheduled: 'warning',
  sending: 'primary',
  sent: 'success',
  cancelled: 'error'
}

// 載入活動
const loadCampaigns = async () => {
  loading.value = true
  try {
    const res = await adminApi.getEmailCampaigns(
      filterStatus.value || undefined,
      currentPage.value,
      perPage
    )
    if (res.success && res.data) {
      // API 可能回傳分頁格式
      if (Array.isArray(res.data)) {
        campaigns.value = res.data
      } else if (res.data.items) {
        campaigns.value = res.data.items
        totalPages.value = res.data.total_pages || 1
      }
    }
  } catch (error) {
    console.error('Failed to load campaigns:', error)
    // 使用模擬資料
    campaigns.value = []
  } finally {
    loading.value = false
  }
}

// 載入範本
const loadTemplates = async () => {
  try {
    const res = await adminApi.getEmailTemplates()
    if (res.success && res.data) {
      templates.value = res.data as EmailTemplate[]
    }
  } catch (error) {
    console.error('Failed to load templates:', error)
  }
}

// 初始載入
onMounted(() => {
  loadCampaigns()
  loadTemplates()
})

// 取得狀態標籤
const getStatusLabel = (status: string): string => {
  return statusLabels[status] || status
}

// 取得狀態樣式
const getStatusVariant = (status: string) => {
  return statusVariants[status] || 'default'
}

// 格式化百分比
const formatPercent = (value?: number): string => {
  if (value === undefined || value === null) return '-'
  return `${(value * 100).toFixed(1)}%`
}

// 格式化日期時間
const formatDateTime = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 重置表單
const resetForm = () => {
  formData.name = ''
  formData.subject = ''
  formData.content = ''
  formData.template_id = ''
  formData.target_audience = 'all'
  formData.scheduled_at = ''
}

// 開啟建立 Modal
const openCreateModal = () => {
  editingCampaign.value = null
  resetForm()
  showModal.value = true
}

// 編輯活動
const editCampaign = (campaign: Campaign) => {
  editingCampaign.value = campaign
  formData.name = campaign.name
  formData.subject = campaign.subject
  formData.content = campaign.content || ''
  formData.template_id = campaign.template_id || ''
  formData.target_audience = campaign.target_audience || 'all'
  formData.scheduled_at = campaign.scheduled_at || ''
  showModal.value = true
}

// 檢視活動
const viewCampaign = (campaign: Campaign) => {
  viewingCampaign.value = campaign
  showDetailModal.value = true
}

// 關閉 Modal
const closeModal = () => {
  showModal.value = false
  editingCampaign.value = null
  resetForm()
}

// 儲存活動
const saveCampaign = async () => {
  if (!formData.name || !formData.subject) {
    alert('請填寫活動名稱和 Email 主旨')
    return
  }

  // 目前 API 尚未實作 create/update，顯示提示
  alert('行銷活動管理功能將於後續版本完整實作。\n\n目前可檢視活動列表與統計資料。')
  closeModal()
}

// 發送活動
const sendCampaign = (campaign: Campaign) => {
  if (confirm(`確定要發送「${campaign.name}」活動嗎？\n\n發送後將無法修改或撤回。`)) {
    alert('發送功能將於後續版本實作。')
  }
}

// 刪除活動
const deleteCampaign = (campaignId: string) => {
  if (confirm('確定要刪除此活動嗎？')) {
    alert('刪除功能將於後續版本實作。')
  }
}

// 分頁
const goToPage = (page: number) => {
  currentPage.value = page
  loadCampaigns()
}

// 返回行銷總覽
const goToMarketing = () => {
  router.push('/admin/marketing')
}
</script>

<style scoped>
.admin-campaigns {
  max-width: 1200px;
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

/* 活動列表 */
.campaigns-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.campaign-item {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-lg);
  background: var(--color-bg);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
}

.campaign-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.campaign-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.campaign-name {
  font-size: var(--font-size-md);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.campaign-meta {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.campaign-subject {
  display: block;
}

.campaign-stats {
  display: flex;
  gap: var(--spacing-lg);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.stat-value {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-primary);
}

.campaign-dates {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.campaign-actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  flex-shrink: 0;
}

/* 分頁 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border-light);
}

.page-info {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* 表單 */
.campaign-form {
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

/* 詳情 */
.campaign-detail {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.detail-row {
  display: flex;
  gap: var(--spacing-md);
}

.detail-row--full {
  flex-direction: column;
}

.detail-label {
  flex-shrink: 0;
  width: 100px;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.detail-value {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.detail-content {
  padding: var(--spacing-md);
  background: var(--color-bg);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  max-height: 300px;
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

  .campaign-item {
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .campaign-actions {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .campaign-stats {
    flex-wrap: wrap;
  }
}
</style>
