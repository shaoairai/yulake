<template>
  <!-- 廠商後台頂部欄 -->
  <header class="admin-topbar">
    <!-- 左側：漢堡選單（小螢幕）+ 店家名稱 -->
    <div class="admin-topbar__left">
      <!-- 漢堡選單按鈕（小螢幕顯示） -->
      <button class="admin-topbar__menu-btn" @click="$emit('toggleSidebar')">
        ☰
      </button>
      <!-- 店家名稱 -->
      <div class="admin-topbar__salon">
        <span class="admin-topbar__salon-name">{{ salonName }}</span>
        <span class="admin-topbar__salon-label">店家後台</span>
      </div>
    </div>

    <!-- 右側：通知與使用者資訊 -->
    <div class="admin-topbar__right">
      <!-- 通知按鈕 -->
      <button class="admin-topbar__notification" @click="handleNotification">
        <span class="admin-topbar__notification-icon">🔔</span>
        <span v-if="notificationCount > 0" class="admin-topbar__notification-badge">
          {{ notificationCount }}
        </span>
      </button>

      <!-- 使用者資訊 -->
      <div class="admin-topbar__user-wrapper">
        <div class="admin-topbar__user" @click="toggleUserMenu">
          <div class="admin-topbar__user-avatar">
            {{ userInitial }}
          </div>
          <div class="admin-topbar__user-info">
            <span class="admin-topbar__user-name">{{ userName }}</span>
            <span class="admin-topbar__user-role">{{ userRole }}</span>
          </div>
          <span class="admin-topbar__user-arrow">▼</span>
        </div>
        <!-- 下拉選單 -->
        <div v-if="showUserMenu" class="admin-topbar__dropdown">
          <button class="admin-topbar__dropdown-item" @click="handleLogout">
            登出
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
/**
 * AdminTopbar - 廠商後台頂部工具列
 * 顯示店家名稱、通知與使用者資訊
 */
import { computed, ref } from 'vue'
import { useAuth } from '~/composables/useAuth'

// 定義事件
defineEmits<{
  toggleSidebar: []
}>()

const router = useRouter()
const { salonUser, salonInfo, logout } = useAuth()

// 下拉選單狀態
const showUserMenu = ref(false)

// 店家名稱
const salonName = computed(() => salonInfo.value?.name || '店家後台')

// 使用者資訊
const userName = computed(() => salonUser.value?.name || '管理員')
const userInitial = computed(() => userName.value.charAt(0))
const userRole = computed(() => {
  const role = salonUser.value?.role
  return role === 'owner' ? '店長' : '員工'
})

// 通知數量
const notificationCount = computed(() => 3)

// 通知按鈕點擊處理
const handleNotification = () => {
  alert('通知功能尚未實作\n\n您有 3 則新通知：\n- 新預約：李小姐預約了基礎凝膠\n- 預約提醒：明日 10:00 有預約\n- 顧客取消：陳小姐取消了預約')
}

// 切換使用者選單
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

// 登出
const handleLogout = () => {
  logout()
  router.push('/admin/login')
}
</script>

<style scoped>
.admin-topbar {
  position: sticky;
  top: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--admin-topbar-height);
  padding: 0 var(--spacing-lg);
  background-color: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border);
  z-index: 50;
}

/* 左側區塊 */
.admin-topbar__left {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.admin-topbar__menu-btn {
  display: none;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0;
  border: none;
  background: transparent;
  border-radius: var(--radius-md);
  font-size: var(--font-size-xl);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.admin-topbar__menu-btn:hover {
  background-color: var(--color-bg-hover);
}

.admin-topbar__salon {
  display: flex;
  flex-direction: column;
}

.admin-topbar__salon-name {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
}

.admin-topbar__salon-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

/* 右側區塊 */
.admin-topbar__right {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

/* 通知按鈕 */
.admin-topbar__notification {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0;
  border: none;
  background: transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.admin-topbar__notification:hover {
  background-color: var(--color-bg-hover);
}

.admin-topbar__notification-icon {
  font-size: var(--font-size-xl);
}

.admin-topbar__notification-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  background-color: var(--color-error);
  color: var(--color-text-inverse);
  font-size: 10px;
  font-weight: 600;
  border-radius: var(--radius-full);
}

/* 使用者資訊 */
.admin-topbar__user {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.admin-topbar__user:hover {
  background-color: var(--color-bg-hover);
}

.admin-topbar__user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  font-size: var(--font-size-sm);
  font-weight: 600;
  border-radius: var(--radius-full);
}

.admin-topbar__user-info {
  display: flex;
  flex-direction: column;
}

.admin-topbar__user-name {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-primary);
}

.admin-topbar__user-role {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.admin-topbar__user-arrow {
  font-size: 10px;
  color: var(--color-text-muted);
}

/* 使用者下拉選單 */
.admin-topbar__user-wrapper {
  position: relative;
}

.admin-topbar__dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: var(--spacing-xs);
  min-width: 120px;
  background-color: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 100;
}

.admin-topbar__dropdown-item {
  display: block;
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  background: transparent;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  text-align: left;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.admin-topbar__dropdown-item:hover {
  background-color: var(--color-bg-hover);
}

/* 響應式：小螢幕 */
@media (max-width: 1024px) {
  .admin-topbar__menu-btn {
    display: flex;
  }

  .admin-topbar__user-info {
    display: none;
  }

  .admin-topbar__user-arrow {
    display: none;
  }
}
</style>
