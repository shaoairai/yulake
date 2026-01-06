<template>
  <!-- 廠商後台 - 會員等級管理 -->
  <div class="admin-membership">
    <!-- 頁面標題 -->
    <AdminPageHeader
      title="會員等級管理"
      description="設定會員等級與升級條件，管理顧客的會員身份。"
    >
      <template #actions>
        <AppButton variant="primary" @click="openAddTierModal">
          ＋ 新增等級
        </AppButton>
      </template>
    </AdminPageHeader>

    <!-- 統計卡片 -->
    <div class="stats-grid">
      <AdminStatCard
        title="總顧客數"
        :value="stats.total_customers"
        icon="👥"
      />
      <AdminStatCard
        title="有等級顧客"
        :value="stats.total_with_tier"
        icon="⭐"
      />
      <AdminStatCard
        title="無等級顧客"
        :value="stats.total_without_tier"
        icon="👤"
      />
    </div>

    <!-- Tab 切換 -->
    <div class="tab-container">
      <button
        :class="['tab-btn', { active: activeTab === 'tiers' }]"
        @click="activeTab = 'tiers'"
      >
        會員等級
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'points' }]"
        @click="activeTab = 'points'"
      >
        集點規則
      </button>
    </div>

    <!-- 會員等級列表 -->
    <AppCard v-if="activeTab === 'tiers'" no-padding>
      <div class="table-wrapper">
        <table class="table">
          <thead>
            <tr>
              <th>等級</th>
              <th>名稱</th>
              <th>升級條件</th>
              <th>折扣</th>
              <th>會員數</th>
              <th>狀態</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tier in tiers" :key="tier.id">
              <td>
                <span class="tier-level" :style="{ backgroundColor: tier.color }">
                  Lv.{{ tier.level }}
                </span>
              </td>
              <td>
                <span class="tier-name">{{ tier.name }}</span>
              </td>
              <td class="tier-conditions">
                <div v-if="tier.min_spent > 0">消費滿 NT$ {{ tier.min_spent.toLocaleString() }}</div>
                <div v-if="tier.min_visits > 0">來店滿 {{ tier.min_visits }} 次</div>
                <div v-if="tier.min_points > 0">集點滿 {{ tier.min_points }} 點</div>
                <div v-if="tier.min_spent === 0 && tier.min_visits === 0 && tier.min_points === 0">
                  無條件（基礎等級）
                </div>
              </td>
              <td>
                <span v-if="tier.discount_percent > 0">{{ 100 - tier.discount_percent }}折</span>
                <span v-else class="text-muted">無折扣</span>
              </td>
              <td>{{ tier.member_count || 0 }} 人</td>
              <td>
                <AppBadge :variant="tier.is_active ? 'success' : 'default'">
                  {{ tier.is_active ? '啟用' : '停用' }}
                </AppBadge>
              </td>
              <td>
                <div class="tier-actions">
                  <AppButton variant="ghost" size="sm" @click="openEditTierModal(tier)">
                    編輯
                  </AppButton>
                  <AppButton
                    variant="ghost"
                    size="sm"
                    @click="toggleTierStatus(tier)"
                  >
                    {{ tier.is_active ? '停用' : '啟用' }}
                  </AppButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 無資料狀態 -->
      <div v-if="tiers.length === 0" class="admin-empty-state">
        <span class="empty-icon">⭐</span>
        <p class="empty-title">尚無會員等級</p>
        <p class="empty-description">點擊「新增等級」按鈕來建立第一個會員等級</p>
      </div>
    </AppCard>

    <!-- 集點規則設定 -->
    <AppCard v-if="activeTab === 'points'" title="集點規則設定">
      <form class="points-form" @submit.prevent="savePointRules">
        <div class="form-group">
          <label class="form-label">
            <input
              v-model="pointRules.is_active"
              type="checkbox"
              class="checkbox-input"
            >
            <span>啟用集點功能</span>
          </label>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">每次來店贈送點數</label>
            <AppInput
              v-model="pointRules.points_per_visit"
              type="number"
              placeholder="10"
            />
          </div>

          <div class="form-group">
            <label class="form-label">消費滿多少元送 1 點</label>
            <AppInput
              v-model="pointRules.points_per_amount"
              type="number"
              placeholder="100"
            />
            <p class="form-hint">設為 0 表示不依消費金額送點</p>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">生日加贈點數</label>
            <AppInput
              v-model="pointRules.bonus_birthday_points"
              type="number"
              placeholder="50"
            />
          </div>

          <div class="form-group">
            <label class="form-label">點數有效期限（月）</label>
            <AppInput
              v-model="pointRules.points_expiry_months"
              type="number"
              placeholder="12"
            />
            <p class="form-hint">設為 0 表示永久有效</p>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">升級規則類型</label>
          <AppSelect v-model="pointRules.upgrade_rule_type">
            <option value="points">依點數升級</option>
            <option value="spent">依消費金額升級</option>
            <option value="visits">依來店次數升級</option>
            <option value="combined">綜合條件升級</option>
          </AppSelect>
        </div>

        <div class="form-actions">
          <AppButton type="submit" variant="primary" :loading="saving">
            儲存設定
          </AppButton>
        </div>
      </form>
    </AppCard>

    <!-- 新增/編輯等級 Modal -->
    <AppModal
      v-model="showTierModal"
      :title="isEditing ? '編輯會員等級' : '新增會員等級'"
      size="md"
    >
      <form class="tier-form" @submit.prevent="handleTierSubmit">
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">
              等級名稱 <span class="required">*</span>
            </label>
            <AppInput
              v-model="tierForm.name"
              placeholder="例如：銀卡會員"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">
              等級順序 <span class="required">*</span>
            </label>
            <AppInput
              v-model="tierForm.level"
              type="number"
              placeholder="1"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">等級顏色</label>
          <input
            v-model="tierForm.color"
            type="color"
            class="color-input"
          >
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">最低累積消費</label>
            <AppInput
              v-model="tierForm.min_spent"
              type="number"
              placeholder="0"
            />
          </div>

          <div class="form-group">
            <label class="form-label">最低來店次數</label>
            <AppInput
              v-model="tierForm.min_visits"
              type="number"
              placeholder="0"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">最低累積點數</label>
            <AppInput
              v-model="tierForm.min_points"
              type="number"
              placeholder="0"
            />
          </div>

          <div class="form-group">
            <label class="form-label">折扣百分比</label>
            <AppInput
              v-model="tierForm.discount_percent"
              type="number"
              placeholder="5"
            />
            <p class="form-hint">輸入 5 表示 95 折</p>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">等級福利說明</label>
          <AppInput
            v-model="tierForm.benefits"
            placeholder="例如：每次消費享 95 折優惠"
          />
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input
              v-model="tierForm.is_active"
              type="checkbox"
              class="checkbox-input"
            >
            <span>啟用此等級</span>
          </label>
        </div>
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="closeTierModal">
          取消
        </AppButton>
        <AppButton variant="primary" :loading="saving" @click="handleTierSubmit">
          {{ isEditing ? '儲存變更' : '新增等級' }}
        </AppButton>
      </template>
    </AppModal>
  </div>
</template>

<script setup lang="ts">
/**
 * 廠商後台 - 會員等級管理頁面
 * 管理會員等級與集點規則
 */
import { ref, reactive, onMounted } from 'vue'
import { useAdminApi } from '~/composables/useAdminApi'
import type { MembershipTier, PointRule } from '~/composables/useAdminApi'

// 設定使用 admin layout 與認證
definePageMeta({
  layout: 'admin',
  middleware: 'auth'
})

const adminApi = useAdminApi()

// Tab 狀態
const activeTab = ref<'tiers' | 'points'>('tiers')

// 載入狀態
const loading = ref(false)
const saving = ref(false)

// 資料
const tiers = ref<MembershipTier[]>([])
const stats = ref({
  total_customers: 0,
  total_with_tier: 0,
  total_without_tier: 0
})
const pointRules = reactive<PointRule>({
  points_per_visit: 10,
  points_per_amount: 100,
  bonus_birthday_points: 50,
  upgrade_rule_type: 'spent',
  points_expiry_months: 12,
  is_active: true
})

// Modal 狀態
const showTierModal = ref(false)
const isEditing = ref(false)
const editingTierId = ref<string | null>(null)

// 等級表單
const tierForm = reactive({
  name: '',
  level: 1,
  min_points: 0,
  min_spent: 0,
  min_visits: 0,
  discount_percent: 0,
  benefits: '',
  color: '#3F7C6A',
  sort_order: 1,
  is_active: true
})

// 載入資料
const loadData = async () => {
  loading.value = true
  try {
    const [tiersRes, statsRes, rulesRes] = await Promise.all([
      adminApi.getMembershipTiers(),
      adminApi.getMembershipStats(),
      adminApi.getPointRules()
    ])

    if (tiersRes.success) {
      tiers.value = tiersRes.data
    }

    if (statsRes.success) {
      stats.value = {
        total_customers: statsRes.data.total_customers || 0,
        total_with_tier: statsRes.data.total_with_tier || 0,
        total_without_tier: statsRes.data.total_without_tier || 0
      }
    }

    if (rulesRes.success && rulesRes.data) {
      Object.assign(pointRules, rulesRes.data)
    }
  } catch (error) {
    console.error('Failed to load membership data:', error)
  } finally {
    loading.value = false
  }
}

// 重置等級表單
const resetTierForm = () => {
  tierForm.name = ''
  tierForm.level = tiers.value.length + 1
  tierForm.min_points = 0
  tierForm.min_spent = 0
  tierForm.min_visits = 0
  tierForm.discount_percent = 0
  tierForm.benefits = ''
  tierForm.color = '#3F7C6A'
  tierForm.sort_order = tiers.value.length + 1
  tierForm.is_active = true
  editingTierId.value = null
}

// 開啟新增等級 Modal
const openAddTierModal = () => {
  resetTierForm()
  isEditing.value = false
  showTierModal.value = true
}

// 開啟編輯等級 Modal
const openEditTierModal = (tier: MembershipTier) => {
  tierForm.name = tier.name
  tierForm.level = tier.level
  tierForm.min_points = tier.min_points
  tierForm.min_spent = tier.min_spent
  tierForm.min_visits = tier.min_visits
  tierForm.discount_percent = tier.discount_percent
  tierForm.benefits = tier.benefits || ''
  tierForm.color = tier.color
  tierForm.sort_order = tier.sort_order
  tierForm.is_active = tier.is_active
  editingTierId.value = tier.id
  isEditing.value = true
  showTierModal.value = true
}

// 關閉等級 Modal
const closeTierModal = () => {
  showTierModal.value = false
  resetTierForm()
}

// 提交等級表單
const handleTierSubmit = async () => {
  if (!tierForm.name.trim()) {
    alert('請輸入等級名稱')
    return
  }

  saving.value = true
  try {
    const data = {
      name: tierForm.name.trim(),
      level: Number(tierForm.level),
      min_points: Number(tierForm.min_points),
      min_spent: Number(tierForm.min_spent),
      min_visits: Number(tierForm.min_visits),
      discount_percent: Number(tierForm.discount_percent),
      benefits: tierForm.benefits.trim(),
      color: tierForm.color,
      sort_order: Number(tierForm.sort_order),
      is_active: tierForm.is_active
    }

    if (isEditing.value && editingTierId.value) {
      const res = await adminApi.updateMembershipTier(editingTierId.value, data)
      if (res.success) {
        alert('等級已更新')
        closeTierModal()
        await loadData()
      } else {
        alert('更新失敗：' + (res.error?.message || '未知錯誤'))
      }
    } else {
      const res = await adminApi.createMembershipTier(data)
      if (res.success) {
        alert('等級已新增')
        closeTierModal()
        await loadData()
      } else {
        alert('新增失敗：' + (res.error?.message || '未知錯誤'))
      }
    }
  } catch (error) {
    console.error('Failed to save tier:', error)
    alert('儲存失敗')
  } finally {
    saving.value = false
  }
}

// 切換等級狀態
const toggleTierStatus = async (tier: MembershipTier) => {
  const action = tier.is_active ? '停用' : '啟用'
  if (!confirm(`確定要${action}「${tier.name}」嗎？`)) return

  try {
    const res = await adminApi.updateMembershipTier(tier.id, {
      is_active: !tier.is_active
    })
    if (res.success) {
      await loadData()
    } else {
      alert('操作失敗')
    }
  } catch (error) {
    console.error('Failed to toggle tier status:', error)
    alert('操作失敗')
  }
}

// 儲存集點規則
const savePointRules = async () => {
  saving.value = true
  try {
    const res = await adminApi.updatePointRules({
      points_per_visit: Number(pointRules.points_per_visit),
      points_per_amount: Number(pointRules.points_per_amount),
      bonus_birthday_points: Number(pointRules.bonus_birthday_points),
      upgrade_rule_type: pointRules.upgrade_rule_type,
      points_expiry_months: Number(pointRules.points_expiry_months),
      is_active: pointRules.is_active
    })

    if (res.success) {
      alert('集點規則已儲存')
    } else {
      alert('儲存失敗：' + (res.error?.message || '未知錯誤'))
    }
  } catch (error) {
    console.error('Failed to save point rules:', error)
    alert('儲存失敗')
  } finally {
    saving.value = false
  }
}

// 初始載入
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.admin-membership {
  max-width: 1200px;
  margin: 0 auto;
}

/* 統計卡片網格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
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

/* 等級標籤 */
.tier-level {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 50px;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-md);
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: white;
}

.tier-name {
  font-weight: 500;
  color: var(--color-text-primary);
}

.tier-conditions {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.tier-actions {
  display: flex;
  gap: var(--spacing-xs);
}

/* 表單樣式 */
.tier-form,
.points-form {
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

.form-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border);
}

/* 顏色選擇器 */
.color-input {
  width: 60px;
  height: 36px;
  padding: 2px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
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

.text-muted {
  color: var(--color-text-muted);
}

/* 響應式 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .table th:nth-child(3),
  .table td:nth-child(3),
  .table th:nth-child(5),
  .table td:nth-child(5) {
    display: none;
  }
}
</style>
