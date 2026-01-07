<template>
  <!-- 顧客註冊頁面 -->
  <div class="auth-page">
    <div class="auth-container">
      <!-- Logo -->
      <div class="auth-logo">
        <div class="logo-icon">Y</div>
        <h1>約來客 <span>Yulake</span></h1>
      </div>

      <!-- 標題 -->
      <h2 class="auth-title">建立帳號</h2>
      <p class="auth-subtitle">加入我們，輕鬆預約美甲美睫服務</p>

      <!-- 錯誤訊息 -->
      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <!-- 註冊表單 -->
      <form class="auth-form" @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="name">姓名</label>
          <input
            id="name"
            v-model="name"
            type="text"
            placeholder="請輸入姓名"
            required
            autocomplete="name"
          >
        </div>

        <div class="form-group">
          <label for="email">電子郵件</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="請輸入電子郵件"
            required
            autocomplete="email"
          >
        </div>

        <div class="form-group">
          <label for="phone">手機號碼（選填）</label>
          <input
            id="phone"
            v-model="phone"
            type="tel"
            placeholder="請輸入手機號碼"
            autocomplete="tel"
          >
        </div>

        <div class="form-group">
          <label for="password">密碼</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="請輸入密碼（至少 6 個字元）"
            required
            minlength="6"
            autocomplete="new-password"
          >
        </div>

        <div class="form-group">
          <label for="confirmPassword">確認密碼</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            placeholder="請再次輸入密碼"
            required
            autocomplete="new-password"
          >
          <span v-if="passwordMismatch" class="field-error">密碼不一致</span>
        </div>

        <button type="submit" class="submit-btn" :disabled="loading || passwordMismatch">
          <span v-if="loading" class="btn-loading" />
          <span v-else>註冊</span>
        </button>
      </form>

      <!-- 登入連結 -->
      <div class="auth-footer">
        <p>已經有帳號？</p>
        <NuxtLink to="/auth/login" class="auth-link">立即登入</NuxtLink>
      </div>

      <!-- 返回連結 -->
      <NuxtLink to="/" class="back-link">← 返回首頁</NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 顧客註冊頁面
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '~/composables/useAuth'

const router = useRouter()
const { customerRegister, loading, error, clearError, isAuthenticated } = useAuth()

// 表單資料
const name = ref('')
const email = ref('')
const phone = ref('')
const password = ref('')
const confirmPassword = ref('')

// 密碼驗證
const passwordMismatch = computed(() => {
  return confirmPassword.value && password.value !== confirmPassword.value
})

// 註冊處理
const handleRegister = async () => {
  if (passwordMismatch.value) return

  clearError()

  const success = await customerRegister(
    name.value,
    email.value,
    password.value,
    phone.value || undefined
  )

  if (success) {
    // 檢查是否有重導向路徑
    const redirectPath = sessionStorage.getItem('redirectAfterLogin')
    if (redirectPath) {
      sessionStorage.removeItem('redirectAfterLogin')
      router.push(redirectPath)
    } else {
      router.push('/my/bookings')
    }
  }
}

// 如果已登入，重導向
onMounted(() => {
  if (isAuthenticated.value) {
    router.push('/my/bookings')
  }
})
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary-light) 0%, var(--color-bg) 100%);
  padding: var(--spacing-lg);
}

.auth-container {
  width: 100%;
  max-width: 400px;
  background: var(--color-bg-card);
  padding: var(--spacing-2xl);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
}

/* Logo */
.auth-logo {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.logo-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  border-radius: var(--radius-lg);
  color: white;
  font-size: 28px;
  font-weight: 700;
  margin-bottom: var(--spacing-sm);
}

.auth-logo h1 {
  font-size: var(--font-size-xl);
  color: var(--color-text-primary);
  margin: 0;
}

.auth-logo h1 span {
  color: var(--color-primary);
  font-weight: 400;
}

/* 標題 */
.auth-title {
  font-size: var(--font-size-xl);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xs) 0;
  text-align: center;
}

.auth-subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-xl) 0;
  text-align: center;
}

/* 錯誤訊息 */
.error-message {
  padding: var(--spacing-md);
  background: var(--color-error-light);
  border: 1px solid var(--color-error);
  border-radius: var(--radius-md);
  color: var(--color-error);
  font-size: var(--font-size-sm);
  text-align: center;
  margin-bottom: var(--spacing-lg);
}

/* 表單 */
.auth-form {
  margin-bottom: var(--spacing-xl);
}

.form-group {
  margin-bottom: var(--spacing-md);
}

.form-group label {
  display: block;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xs);
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-md);
  font-family: inherit;
  background: var(--color-bg);
  transition: border-color var(--transition-fast);
}

.form-group input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.form-group input::placeholder {
  color: var(--color-text-muted);
}

.field-error {
  display: block;
  margin-top: var(--spacing-xs);
  font-size: var(--font-size-xs);
  color: var(--color-error);
}

.submit-btn {
  width: 100%;
  padding: var(--spacing-md);
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  font-size: var(--font-size-md);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
}

.submit-btn:disabled {
  background: var(--color-border);
  cursor: not-allowed;
}

.submit-btn:not(:disabled):hover {
  opacity: 0.9;
}

.btn-loading {
  width: 20px;
  height: 20px;
  border: 2px solid white;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Footer */
.auth-footer {
  text-align: center;
  margin-bottom: var(--spacing-lg);
}

.auth-footer p {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-xs) 0;
}

.auth-link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 500;
}

.auth-link:hover {
  text-decoration: underline;
}

/* 返回連結 */
.back-link {
  display: block;
  text-align: center;
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: var(--font-size-sm);
}

.back-link:hover {
  color: var(--color-primary);
}
</style>
