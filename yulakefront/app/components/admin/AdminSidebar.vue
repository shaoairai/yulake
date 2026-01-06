<template>
  <!-- 廠商後台側邊欄 -->
  <aside class="admin-sidebar">
    <!-- Logo 區塊 -->
    <div class="admin-sidebar__logo">
      <div class="admin-sidebar__logo-icon">Y</div>
      <div class="admin-sidebar__logo-text">
        <span class="admin-sidebar__logo-title">約來客</span>
        <span class="admin-sidebar__logo-subtitle">yulake</span>
      </div>
    </div>

    <!-- 導航選單 -->
    <nav class="admin-sidebar__nav">
      <NuxtLink
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        :class="[
          'admin-sidebar__nav-item',
          { 'admin-sidebar__nav-item--active': isActive(item.path) }
        ]"
      >
        <span class="admin-sidebar__nav-icon">{{ item.icon }}</span>
        <span class="admin-sidebar__nav-label">{{ item.label }}</span>
      </NuxtLink>
    </nav>

    <!-- 底部店家資訊 -->
    <div class="admin-sidebar__footer">
      <div class="admin-sidebar__salon-info">
        <span class="admin-sidebar__salon-name">{{ salonName }}</span>
        <span class="admin-sidebar__salon-status">營業中</span>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
/**
 * AdminSidebar - 廠商後台左側導航欄
 * 提供主要的後台功能導航
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'

// 導航項目定義
const navItems = [
  { path: '/admin', label: '今日總覽', icon: '📊' },
  { path: '/admin/calendar', label: '預約日曆', icon: '📆' },
  { path: '/admin/bookings', label: '預約管理', icon: '📅' },
  { path: '/admin/customers', label: '顧客與黑名單', icon: '👥' },
  { path: '/admin/services', label: '服務與價目', icon: '💅' },
  { path: '/admin/stylists', label: '設計師管理', icon: '✨' },
  { path: '/admin/membership', label: '會員等級', icon: '⭐' },
  { path: '/admin/marketing', label: 'Email 行銷', icon: '📧' },
  { path: '/admin/settings', label: '店家設定', icon: '⚙️' }
]

// 取得當前路由
const route = useRoute()

// 判斷導航項目是否為當前頁面
const isActive = (path: string): boolean => {
  if (path === '/admin') {
    return route.path === '/admin'
  }
  return route.path.startsWith(path)
}

// 店家名稱（之後會從 composable 取得）
const salonName = computed(() => '霧光美甲工作室')
</script>

<style scoped>
.admin-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: var(--admin-sidebar-width);
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--color-bg-card);
  border-right: 1px solid var(--color-border);
  z-index: 100;
}

/* Logo 區塊 */
.admin-sidebar__logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.admin-sidebar__logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  border-radius: var(--radius-md);
  color: var(--color-text-inverse);
  font-size: var(--font-size-xl);
  font-weight: 700;
}

.admin-sidebar__logo-text {
  display: flex;
  flex-direction: column;
}

.admin-sidebar__logo-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
}

.admin-sidebar__logo-subtitle {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  text-transform: lowercase;
}

/* 導航選單 */
.admin-sidebar__nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: var(--spacing-md);
  gap: var(--spacing-xs);
  overflow-y: auto;
}

.admin-sidebar__nav-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: all var(--transition-fast);
}

.admin-sidebar__nav-item:hover {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

.admin-sidebar__nav-item--active {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: 500;
}

.admin-sidebar__nav-icon {
  font-size: var(--font-size-lg);
  width: 24px;
  text-align: center;
}

.admin-sidebar__nav-label {
  font-size: var(--font-size-sm);
}

/* 底部店家資訊 */
.admin-sidebar__footer {
  padding: var(--spacing-md) var(--spacing-lg);
  border-top: 1px solid var(--color-border-light);
}

.admin-sidebar__salon-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.admin-sidebar__salon-name {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.admin-sidebar__salon-status {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: var(--font-size-xs);
  color: var(--color-success);
}

.admin-sidebar__salon-status::before {
  content: '';
  display: inline-block;
  width: 6px;
  height: 6px;
  background-color: var(--color-success);
  border-radius: 50%;
}

/* 響應式：小螢幕隱藏側邊欄 */
@media (max-width: 1024px) {
  .admin-sidebar {
    transform: translateX(-100%);
    transition: transform var(--transition-normal);
  }

  .admin-sidebar--open {
    transform: translateX(0);
  }
}
</style>
