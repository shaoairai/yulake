<template>
  <!-- 首頁 - 平台入口頁面 -->
  <div class="home-page">
    <!-- Hero 區塊 -->
    <section class="hero">
      <div class="hero-content">
        <div class="logo">Y</div>
        <h1>約來客 <span class="brand-en">Yulake</span></h1>
        <p class="tagline">美甲美睫預約平台</p>
        <p class="description">輕鬆管理您的預約，隨時查看排程</p>
      </div>
    </section>

    <!-- 快速入口 -->
    <section class="quick-links">
      <NuxtLink to="/my/bookings" class="link-card customer">
        <span class="link-icon">📅</span>
        <span class="link-title">我的預約</span>
        <span class="link-desc">查看及管理您的預約紀錄</span>
      </NuxtLink>

      <NuxtLink to="/admin" class="link-card admin">
        <span class="link-icon">🏪</span>
        <span class="link-title">店家後台</span>
        <span class="link-desc">店家管理系統入口</span>
      </NuxtLink>
    </section>

    <!-- 底部資訊 -->
    <footer class="home-footer">
      <p>&copy; 2026 約來客 Yulake. All rights reserved.</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
/**
 * 首頁 - 平台入口頁面
 * 提供顧客與店家的快速入口
 */
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--color-bg);
}

/* Hero 區塊 */
.hero {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  background: linear-gradient(135deg, var(--color-primary-light) 0%, var(--color-bg) 100%);
}

.hero-content {
  text-align: center;
}

.logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  border-radius: var(--radius-xl);
  color: var(--color-text-inverse);
  font-size: 40px;
  font-weight: 700;
  margin-bottom: var(--spacing-lg);
  box-shadow: var(--shadow-lg);
}

h1 {
  font-size: var(--font-size-3xl);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm) 0;
}

.brand-en {
  color: var(--color-primary);
  font-weight: 400;
}

.tagline {
  font-size: var(--font-size-lg);
  color: var(--color-primary);
  font-weight: 500;
  margin: 0 0 var(--spacing-xs) 0;
}

.description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

/* 快速入口 */
.quick-links {
  display: flex;
  gap: var(--spacing-lg);
  justify-content: center;
  padding: var(--spacing-2xl);
  background-color: var(--color-bg-card);
}

.link-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xl) var(--spacing-2xl);
  background-color: var(--color-bg);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-lg);
  text-decoration: none;
  transition: all var(--transition-fast);
  min-width: 200px;
}

.link-card:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.link-card.customer:hover {
  border-color: var(--color-primary);
  background-color: var(--color-primary-light);
}

.link-card.admin:hover {
  border-color: var(--color-secondary);
}

.link-icon {
  font-size: 32px;
}

.link-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
}

.link-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  text-align: center;
}

/* 底部 */
.home-footer {
  padding: var(--spacing-lg);
  text-align: center;
  background-color: var(--color-bg);
  border-top: 1px solid var(--color-border-light);
}

.home-footer p {
  margin: 0;
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

/* 響應式 */
@media (max-width: 768px) {
  .quick-links {
    flex-direction: column;
    align-items: center;
  }

  .link-card {
    width: 100%;
    max-width: 300px;
  }

  h1 {
    font-size: var(--font-size-2xl);
  }
}
</style>
