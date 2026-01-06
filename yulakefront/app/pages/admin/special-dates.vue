<template>
  <!-- 廠商後台 - 特殊日期管理 -->
  <div class="admin-special-dates">
    <!-- 頁面標題 -->
    <AdminPageHeader
      title="特殊日期管理"
      description="設定店休日、特殊營業時間等"
    >
      <template #actions>
        <AppButton variant="primary" size="sm" @click="openCreateModal">
          ＋ 新增特殊日期
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
      <div class="filter-group">
        <label>日期範圍</label>
        <div class="date-range">
          <AppInput
            v-model="filterStartDate"
            type="date"
            placeholder="起始日期"
          />
          <span class="date-range-separator">～</span>
          <AppInput
            v-model="filterEndDate"
            type="date"
            placeholder="結束日期"
          />
        </div>
      </div>
      <AppButton variant="outline" size="sm" @click="applyFilter">
        套用篩選
      </AppButton>
    </div>

    <!-- 特殊日期列表 -->
    <AppCard>
      <div v-if="loading" class="loading-state">
        載入中...
      </div>
      <div v-else-if="filteredDates.length === 0" class="empty-state">
        <p>尚無特殊日期設定</p>
        <AppButton variant="primary" size="sm" @click="openCreateModal">
          新增第一個特殊日期
        </AppButton>
      </div>
      <div v-else class="special-dates-list">
        <div
          v-for="item in filteredDates"
          :key="item.id"
          class="special-date-item"
          :class="{ 'special-date-item--closed': item.type === 'closed' }"
        >
          <div class="special-date-info">
            <div class="special-date-date">
              {{ formatDate(item.date) }}
            </div>
            <div class="special-date-type">
              <AppBadge :variant="item.type === 'closed' ? 'error' : 'warning'">
                {{ item.type === 'closed' ? '店休日' : '特殊營業時間' }}
              </AppBadge>
            </div>
            <div v-if="item.description" class="special-date-description">
              {{ item.description }}
            </div>
            <div v-if="item.type === 'special_hours' && item.open_time && item.close_time" class="special-date-hours">
              營業時間：{{ item.open_time }} - {{ item.close_time }}
            </div>
          </div>
          <div class="special-date-actions">
            <AppButton variant="ghost" size="sm" @click="editSpecialDate(item)">
              編輯
            </AppButton>
            <AppButton variant="ghost" size="sm" @click="deleteSpecialDateAction(item.id)">
              刪除
            </AppButton>
          </div>
        </div>
      </div>
    </AppCard>

    <!-- 新增/編輯 Modal -->
    <AppModal
      v-model="showModal"
      :title="editingDate ? '編輯特殊日期' : '新增特殊日期'"
    >
      <form class="special-date-form" @submit.prevent="saveSpecialDate">
        <div class="form-group">
          <label class="form-label">日期 <span class="required">*</span></label>
          <AppInput
            v-model="formData.date"
            type="date"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label">類型 <span class="required">*</span></label>
          <AppSelect
            v-model="formData.type"
            :options="[
              { value: 'closed', label: '店休日' },
              { value: 'special_hours', label: '特殊營業時間' }
            ]"
            required
          />
        </div>

        <template v-if="formData.type === 'special_hours'">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">開始時間</label>
              <AppInput
                v-model="formData.open_time"
                type="time"
              />
            </div>
            <div class="form-group">
              <label class="form-label">結束時間</label>
              <AppInput
                v-model="formData.close_time"
                type="time"
              />
            </div>
          </div>
        </template>

        <div class="form-group">
          <label class="form-label">說明</label>
          <AppInput
            v-model="formData.description"
            placeholder="例如：國定假日、店家活動等"
          />
        </div>
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="closeModal">
          取消
        </AppButton>
        <AppButton variant="primary" @click="saveSpecialDate">
          {{ editingDate ? '更新' : '新增' }}
        </AppButton>
      </template>
    </AppModal>
  </div>
</template>

<script setup lang="ts">
/**
 * 廠商後台 - 特殊日期管理頁面
 * 管理店休日、特殊營業時間等
 */
import { ref, computed, reactive, onMounted } from 'vue'
import { useAdminApi } from '~/composables/useAdminApi'
import type { SpecialDate } from '~/composables/useAdminApi'

// 設定使用 admin layout 與認證
definePageMeta({
  layout: 'admin',
  middleware: 'auth'
})

// API
const adminApi = useAdminApi()

// 本地狀態
const loading = ref(false)
const specialDates = ref<SpecialDate[]>([])
const showModal = ref(false)
const editingDate = ref<SpecialDate | null>(null)

// 篩選狀態
const filterType = ref('')
const filterStartDate = ref('')
const filterEndDate = ref('')

// 類型選項
const typeOptions = [
  { value: '', label: '全部類型' },
  { value: 'closed', label: '店休日' },
  { value: 'special_hours', label: '特殊營業時間' }
]

// 表單資料
const formData = reactive({
  date: '',
  type: 'closed' as 'closed' | 'special_hours',
  description: '',
  open_time: '',
  close_time: ''
})

// 載入特殊日期
const loadSpecialDates = async () => {
  loading.value = true
  try {
    const res = await adminApi.getSpecialDates(filterStartDate.value || undefined, filterEndDate.value || undefined)
    if (res.success && res.data) {
      specialDates.value = res.data
    }
  } catch (error) {
    console.error('Failed to load special dates:', error)
  } finally {
    loading.value = false
  }
}

// 初始載入
onMounted(() => {
  // 預設顯示今天起 90 天的特殊日期
  const today = new Date()
  filterStartDate.value = today.toISOString().split('T')[0]
  const endDate = new Date()
  endDate.setDate(endDate.getDate() + 90)
  filterEndDate.value = endDate.toISOString().split('T')[0]
  loadSpecialDates()
})

// 篩選後的日期
const filteredDates = computed(() => {
  return specialDates.value.filter(item => {
    if (filterType.value && item.type !== filterType.value) {
      return false
    }
    return true
  }).sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
})

// 套用篩選
const applyFilter = () => {
  loadSpecialDates()
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

// 重置表單
const resetForm = () => {
  formData.date = ''
  formData.type = 'closed'
  formData.description = ''
  formData.open_time = ''
  formData.close_time = ''
}

// 開啟新增 Modal
const openCreateModal = () => {
  editingDate.value = null
  resetForm()
  showModal.value = true
}

// 編輯特殊日期
const editSpecialDate = (item: SpecialDate) => {
  editingDate.value = item
  formData.date = item.date
  formData.type = item.type
  formData.description = item.description || ''
  formData.open_time = item.open_time || ''
  formData.close_time = item.close_time || ''
  showModal.value = true
}

// 關閉 Modal
const closeModal = () => {
  showModal.value = false
  editingDate.value = null
  resetForm()
}

// 儲存特殊日期
const saveSpecialDate = async () => {
  if (!formData.date || !formData.type) {
    alert('請填寫必要欄位')
    return
  }

  try {
    if (editingDate.value) {
      // 更新
      const res = await adminApi.updateSpecialDate(editingDate.value.id, {
        date: formData.date,
        type: formData.type,
        description: formData.description || undefined,
        open_time: formData.type === 'special_hours' ? formData.open_time : undefined,
        close_time: formData.type === 'special_hours' ? formData.close_time : undefined
      })
      if (res.success) {
        await loadSpecialDates()
        closeModal()
      } else {
        alert('更新失敗，請稍後再試')
      }
    } else {
      // 新增
      const res = await adminApi.createSpecialDate({
        date: formData.date,
        type: formData.type,
        description: formData.description || undefined,
        open_time: formData.type === 'special_hours' ? formData.open_time : undefined,
        close_time: formData.type === 'special_hours' ? formData.close_time : undefined
      })
      if (res.success) {
        await loadSpecialDates()
        closeModal()
      } else {
        alert('新增失敗，請稍後再試')
      }
    }
  } catch (error) {
    console.error('Failed to save special date:', error)
    alert('操作失敗，請稍後再試')
  }
}

// 刪除特殊日期
const deleteSpecialDateAction = async (dateId: string) => {
  if (!confirm('確定要刪除此特殊日期嗎？')) {
    return
  }

  try {
    const res = await adminApi.deleteSpecialDate(dateId)
    if (res.success) {
      await loadSpecialDates()
    } else {
      alert('刪除失敗，請稍後再試')
    }
  } catch (error) {
    console.error('Failed to delete special date:', error)
    alert('刪除失敗，請稍後再試')
  }
}
</script>

<style scoped>
.admin-special-dates {
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
  min-width: 140px;
}

.filter-group label {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
}

.date-range {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.date-range-separator {
  color: var(--color-text-muted);
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

/* 特殊日期列表 */
.special-dates-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.special-date-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md);
  background: var(--color-bg);
  border-radius: var(--radius-md);
  border-left: 4px solid var(--color-warning);
}

.special-date-item--closed {
  border-left-color: var(--color-error);
}

.special-date-info {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--spacing-md);
}

.special-date-date {
  font-weight: 600;
  color: var(--color-text-primary);
  min-width: 140px;
}

.special-date-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.special-date-hours {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.special-date-actions {
  display: flex;
  gap: var(--spacing-xs);
  flex-shrink: 0;
}

/* 表單 */
.special-date-form {
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

/* 響應式 */
@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group {
    min-width: auto;
  }

  .date-range {
    flex-direction: column;
    align-items: stretch;
  }

  .date-range-separator {
    text-align: center;
  }

  .special-date-item {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }

  .special-date-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
