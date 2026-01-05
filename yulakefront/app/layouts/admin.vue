<template>
  <!-- 廠商後台 Layout -->
  <div class="admin-layout">
    <!-- 左側側邊欄 -->
    <AdminSidebar />

    <!-- 右側主內容區 -->
    <div class="admin-layout__main">
      <!-- 頂部工具列 -->
      <AdminTopbar @toggle-sidebar="toggleSidebar" />

      <!-- 頁面內容區 -->
      <main class="admin-layout__content">
        <slot />
      </main>
    </div>

    <!-- 行動版側邊欄遮罩 -->
    <div
      v-if="isSidebarOpen"
      class="admin-layout__overlay"
      @click="closeSidebar"
    ></div>
  </div>
</template>

<script setup lang="ts">
/**
 * Admin Layout - 廠商後台共用版面配置
 * 包含左側側邊欄與右側主內容區
 */
import { ref } from 'vue'

// 側邊欄開關狀態（用於行動版）
const isSidebarOpen = ref(false)

// 切換側邊欄
const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

// 關閉側邊欄
const closeSidebar = () => {
  isSidebarOpen.value = false
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--color-bg);
}

/* 主內容區 */
.admin-layout__main {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: var(--admin-sidebar-width);
  min-width: 0;
}

/* 內容區 */
.admin-layout__content {
  flex: 1;
  padding: var(--spacing-lg);
  overflow-y: auto;
}

/* 行動版遮罩 */
.admin-layout__overlay {
  display: none;
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 90;
}

/* 響應式：小螢幕 */
@media (max-width: 1024px) {
  .admin-layout__main {
    margin-left: 0;
  }

  .admin-layout__overlay {
    display: block;
  }
}
</style>
