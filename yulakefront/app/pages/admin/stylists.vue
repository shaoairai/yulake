<template>
  <!-- 廠商後台 - 設計師管理 -->
  <div class="admin-stylists">
    <!-- 頁面標題 -->
    <AdminPageHeader
      title="設計師管理"
      description="管理設計師基本資料與擅長風格。"
    >
      <template #actions>
        <AppButton variant="primary" @click="openAddModal">
          ＋ 新增設計師
        </AppButton>
      </template>
    </AdminPageHeader>

    <!-- 設計師列表 -->
    <div class="stylist-grid">
      <AppCard
        v-for="stylist in stylists"
        :key="stylist.id"
        class="stylist-card"
        hoverable
      >
        <div class="stylist-header">
          <div class="stylist-avatar">
            {{ stylist.name.charAt(0) }}
          </div>
          <div class="stylist-info">
            <h3 class="stylist-name">{{ stylist.name }}</h3>
            <span class="stylist-style">{{ stylist.style }}</span>
          </div>
          <AppBadge :variant="stylist.isActive ? 'success' : 'default'" size="sm">
            {{ stylist.isActive ? '已啟用' : '已停用' }}
          </AppBadge>
        </div>

        <p class="stylist-intro">{{ stylist.introduction }}</p>

        <div class="stylist-schedule">
          <span class="schedule-icon">📅</span>
          <span class="schedule-text">出勤時間設定將於之後版本提供</span>
        </div>

        <template #footer>
          <div class="stylist-actions">
            <AppButton variant="ghost" size="sm" @click="openEditModal(stylist)">
              編輯
            </AppButton>
            <AppButton
              variant="ghost"
              size="sm"
              @click="toggleStylistStatus(stylist)"
            >
              {{ stylist.isActive ? '停用' : '啟用' }}
            </AppButton>
          </div>
        </template>
      </AppCard>
    </div>

    <!-- 無資料狀態 -->
    <AppCard v-if="stylists.length === 0">
      <div class="admin-empty-state">
        <span class="empty-icon">✨</span>
        <p class="empty-title">尚無設計師</p>
        <p class="empty-description">點擊「新增設計師」按鈕來建立第一位設計師</p>
      </div>
    </AppCard>

    <!-- 新增/編輯設計師 Modal -->
    <AppModal
      v-model="showModal"
      :title="isEditing ? '編輯設計師' : '新增設計師'"
      size="md"
    >
      <form class="stylist-form" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label class="form-label">
            姓名 <span class="required">*</span>
          </label>
          <AppInput
            v-model="formData.name"
            placeholder="例如：Amy"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label">
            擅長風格 <span class="required">*</span>
          </label>
          <AppInput
            v-model="formData.style"
            placeholder="例如：日系清新、簡約法式"
            required
          />
          <p class="form-hint">多種風格可用頓號分隔</p>
        </div>

        <div class="form-group">
          <label class="form-label">簡介</label>
          <textarea
            v-model="formData.introduction"
            class="form-textarea"
            placeholder="簡短介紹設計師的經歷與特色"
            rows="3"
          ></textarea>
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input
              v-model="formData.isActive"
              type="checkbox"
              class="checkbox-input"
            >
            <span>啟用此設計師</span>
          </label>
        </div>
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="closeModal">
          取消
        </AppButton>
        <AppButton variant="primary" @click="handleSubmit">
          {{ isEditing ? '儲存變更' : '新增設計師' }}
        </AppButton>
      </template>
    </AppModal>
  </div>
</template>

<script setup lang="ts">
/**
 * 廠商後台 - 設計師管理頁面
 * 提供設計師的新增、編輯與狀態管理
 */
import { ref, reactive } from 'vue'
import { useAdminMockData } from '~/composables/useAdminMockData'
import type { Stylist } from '~/composables/useAdminMockData'

// 設定使用 admin layout 與認證
definePageMeta({
  layout: 'admin',
  middleware: 'auth'
})

// 取得假資料
const { stylists, addStylist, updateStylist } = useAdminMockData()

// Modal 狀態
const showModal = ref(false)
const isEditing = ref(false)
const editingStylistId = ref<string | null>(null)

// 表單資料
const formData = reactive({
  name: '',
  style: '',
  introduction: '',
  isActive: true
})

// 重置表單
const resetForm = () => {
  formData.name = ''
  formData.style = ''
  formData.introduction = ''
  formData.isActive = true
  editingStylistId.value = null
}

// 開啟新增 Modal
const openAddModal = () => {
  resetForm()
  isEditing.value = false
  showModal.value = true
}

// 開啟編輯 Modal
const openEditModal = (stylist: Stylist) => {
  formData.name = stylist.name
  formData.style = stylist.style
  formData.introduction = stylist.introduction
  formData.isActive = stylist.isActive
  editingStylistId.value = stylist.id
  isEditing.value = true
  showModal.value = true
}

// 關閉 Modal
const closeModal = () => {
  showModal.value = false
  resetForm()
}

// 提交表單
const handleSubmit = () => {
  // 驗證必填欄位
  if (!formData.name.trim()) {
    alert('請輸入設計師姓名')
    return
  }
  if (!formData.style.trim()) {
    alert('請輸入擅長風格')
    return
  }

  const stylistData = {
    name: formData.name.trim(),
    style: formData.style.trim(),
    introduction: formData.introduction.trim(),
    isActive: formData.isActive
  }

  if (isEditing.value && editingStylistId.value) {
    // 更新設計師
    updateStylist(editingStylistId.value, stylistData)
    alert('設計師資料已更新')
  } else {
    // 新增設計師
    addStylist(stylistData)
    alert('設計師已新增')
  }

  closeModal()
}

// 切換設計師狀態
const toggleStylistStatus = (stylist: Stylist) => {
  const action = stylist.isActive ? '停用' : '啟用'
  if (confirm(`確定要${action}「${stylist.name}」嗎？`)) {
    updateStylist(stylist.id, { isActive: !stylist.isActive })
  }
}
</script>

<style scoped>
.admin-stylists {
  max-width: 1200px;
  margin: 0 auto;
}

/* 設計師網格 */
.stylist-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-lg);
}

/* 設計師卡片 */
.stylist-card {
  display: flex;
  flex-direction: column;
}

.stylist-header {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.stylist-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  border-radius: var(--radius-lg);
  color: var(--color-text-inverse);
  font-size: var(--font-size-xl);
  font-weight: 600;
  flex-shrink: 0;
}

.stylist-info {
  flex: 1;
  min-width: 0;
}

.stylist-name {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
}

.stylist-style {
  font-size: var(--font-size-sm);
  color: var(--color-primary);
}

.stylist-intro {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  margin: 0 0 var(--spacing-md) 0;
  flex: 1;
}

.stylist-schedule {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm);
  background: var(--color-bg);
  border-radius: var(--radius-md);
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.schedule-icon {
  font-size: var(--font-size-base);
}

.stylist-actions {
  display: flex;
  gap: var(--spacing-sm);
}

/* 表單樣式 */
.stylist-form {
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
  font-family: inherit;
  font-size: var(--font-size-sm);
  resize: vertical;
  outline: none;
  transition: border-color var(--transition-fast);
}

.form-textarea:focus {
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
@media (max-width: 1024px) {
  .stylist-grid {
    grid-template-columns: 1fr;
  }
}
</style>
