<template>
  <!-- 廠商後台 - 服務與價目管理 -->
  <div class="admin-services">
    <!-- 頁面標題 -->
    <AdminPageHeader
      title="服務與價目"
      description="管理可提供的服務項目與時間、價格。"
    >
      <template #actions>
        <AppButton variant="primary" @click="openAddModal">
          ＋ 新增服務
        </AppButton>
      </template>
    </AdminPageHeader>

    <!-- 服務列表 -->
    <AppCard no-padding>
      <div class="table-wrapper">
        <table class="table">
          <thead>
            <tr>
              <th>服務名稱</th>
              <th>說明</th>
              <th>耗時</th>
              <th>價格</th>
              <th>適用設計師</th>
              <th>狀態</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="service in services" :key="service.id">
              <td>
                <span class="service-name">{{ service.name }}</span>
              </td>
              <td>
                <span class="service-description">{{ service.description }}</span>
              </td>
              <td>{{ service.duration }} 分鐘</td>
              <td>NT$ {{ service.price.toLocaleString() }}</td>
              <td>
                <span class="service-stylists">{{ service.stylists }}</span>
              </td>
              <td>
                <AppBadge :variant="service.isActive ? 'success' : 'default'">
                  {{ service.isActive ? '已啟用' : '已停用' }}
                </AppBadge>
              </td>
              <td>
                <div class="service-actions">
                  <AppButton variant="ghost" size="sm" @click="openEditModal(service)">
                    編輯
                  </AppButton>
                  <AppButton
                    variant="ghost"
                    size="sm"
                    @click="toggleServiceStatus(service)"
                  >
                    {{ service.isActive ? '停用' : '啟用' }}
                  </AppButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 無資料狀態 -->
      <div v-if="services.length === 0" class="admin-empty-state">
        <span class="empty-icon">💅</span>
        <p class="empty-title">尚無服務項目</p>
        <p class="empty-description">點擊「新增服務」按鈕來建立第一個服務</p>
      </div>
    </AppCard>

    <!-- 新增/編輯服務 Modal -->
    <AppModal
      v-model="showModal"
      :title="isEditing ? '編輯服務' : '新增服務'"
      size="md"
    >
      <form class="service-form" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label class="form-label">
            服務名稱 <span class="required">*</span>
          </label>
          <AppInput
            v-model="formData.name"
            placeholder="例如：基礎手部凝膠"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label">服務說明</label>
          <AppInput
            v-model="formData.description"
            placeholder="簡短描述此服務內容"
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">
              耗時（分鐘） <span class="required">*</span>
            </label>
            <AppInput
              v-model="formData.duration"
              type="number"
              placeholder="60"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">
              價格（NT$） <span class="required">*</span>
            </label>
            <AppInput
              v-model="formData.price"
              type="number"
              placeholder="800"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">適用設計師</label>
          <AppInput
            v-model="formData.stylists"
            placeholder="例如：全部設計師、或 Amy / Bella"
          />
          <p class="form-hint">留空則預設為全部設計師</p>
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input
              v-model="formData.isActive"
              type="checkbox"
              class="checkbox-input"
            >
            <span>啟用此服務</span>
          </label>
        </div>
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="closeModal">
          取消
        </AppButton>
        <AppButton variant="primary" @click="handleSubmit">
          {{ isEditing ? '儲存變更' : '新增服務' }}
        </AppButton>
      </template>
    </AppModal>
  </div>
</template>

<script setup lang="ts">
/**
 * 廠商後台 - 服務與價目管理頁面
 * 提供服務項目的新增、編輯與狀態管理
 */
import { ref, reactive } from 'vue'
import { useAdminMockData } from '~/composables/useAdminMockData'
import type { Service } from '~/composables/useAdminMockData'

// 設定使用 admin layout 與認證
definePageMeta({
  layout: 'admin',
  middleware: 'auth'
})

// 取得假資料
const { services, addService, updateService } = useAdminMockData()

// Modal 狀態
const showModal = ref(false)
const isEditing = ref(false)
const editingServiceId = ref<string | null>(null)

// 表單資料
const formData = reactive({
  name: '',
  description: '',
  duration: 60,
  price: 800,
  stylists: '',
  isActive: true
})

// 重置表單
const resetForm = () => {
  formData.name = ''
  formData.description = ''
  formData.duration = 60
  formData.price = 800
  formData.stylists = ''
  formData.isActive = true
  editingServiceId.value = null
}

// 開啟新增 Modal
const openAddModal = () => {
  resetForm()
  isEditing.value = false
  showModal.value = true
}

// 開啟編輯 Modal
const openEditModal = (service: Service) => {
  formData.name = service.name
  formData.description = service.description
  formData.duration = service.duration
  formData.price = service.price
  formData.stylists = service.stylists
  formData.isActive = service.isActive
  editingServiceId.value = service.id
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
    alert('請輸入服務名稱')
    return
  }
  if (!formData.duration || formData.duration <= 0) {
    alert('請輸入有效的服務時長')
    return
  }
  if (!formData.price || formData.price <= 0) {
    alert('請輸入有效的價格')
    return
  }

  const serviceData = {
    name: formData.name.trim(),
    description: formData.description.trim(),
    duration: Number(formData.duration),
    price: Number(formData.price),
    stylists: formData.stylists.trim() || '全部設計師',
    isActive: formData.isActive
  }

  if (isEditing.value && editingServiceId.value) {
    // 更新服務
    updateService(editingServiceId.value, serviceData)
    alert('服務已更新')
  } else {
    // 新增服務
    addService(serviceData)
    alert('服務已新增')
  }

  closeModal()
}

// 切換服務狀態
const toggleServiceStatus = (service: Service) => {
  const action = service.isActive ? '停用' : '啟用'
  if (confirm(`確定要${action}「${service.name}」嗎？`)) {
    updateService(service.id, { isActive: !service.isActive })
  }
}
</script>

<style scoped>
.admin-services {
  max-width: 1200px;
  margin: 0 auto;
}

/* 服務名稱 */
.service-name {
  font-weight: 500;
  color: var(--color-text-primary);
}

/* 服務說明 */
.service-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 適用設計師 */
.service-stylists {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* 操作按鈕 */
.service-actions {
  display: flex;
  gap: var(--spacing-xs);
}

/* 表單樣式 */
.service-form {
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

  .table th:nth-child(2),
  .table td:nth-child(2),
  .table th:nth-child(5),
  .table td:nth-child(5) {
    display: none;
  }
}
</style>
