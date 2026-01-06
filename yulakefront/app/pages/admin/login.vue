<script setup lang="ts">
/**
 * 店家登入頁面
 */
import { ref } from 'vue'
import { useAuth } from '~/composables/useAuth'

definePageMeta({
  layout: false
})

const { salonLogin, loading, error, clearError } = useAuth()
const router = useRouter()

const email = ref('')
const password = ref('')
const showPassword = ref(false)

const handleLogin = async () => {
  clearError()

  if (!email.value || !password.value) {
    return
  }

  const success = await salonLogin(email.value, password.value)

  if (success) {
    router.push('/admin')
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Logo 區域 -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-primary-600 mb-2">約來客</h1>
        <p class="text-gray-600">店家管理後台</p>
      </div>

      <!-- 登入表單 -->
      <div class="bg-white rounded-2xl shadow-xl p-8">
        <h2 class="text-xl font-semibold text-gray-800 mb-6">登入</h2>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <!-- Email -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
              電子郵件
            </label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
              placeholder="請輸入 Email"
              :disabled="loading"
            />
          </div>

          <!-- 密碼 -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
              密碼
            </label>
            <div class="relative">
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                required
                class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors pr-12"
                placeholder="請輸入密碼"
                :disabled="loading"
              />
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                @click="showPassword = !showPassword"
              >
                <span v-if="showPassword">隱藏</span>
                <span v-else>顯示</span>
              </button>
            </div>
          </div>

          <!-- 錯誤訊息 -->
          <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
            {{ error }}
          </div>

          <!-- 登入按鈕 -->
          <button
            type="submit"
            class="w-full py-3 px-4 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="loading || !email || !password"
          >
            <span v-if="loading">登入中...</span>
            <span v-else>登入</span>
          </button>
        </form>

        <!-- 測試帳號提示（開發用） -->
        <div class="mt-6 pt-6 border-t border-gray-200">
          <p class="text-xs text-gray-500 text-center mb-2">開發測試帳號</p>
          <div class="bg-gray-50 rounded-lg p-3 text-xs text-gray-600">
            <p>Email: admin@nailart.com</p>
            <p>Password: password123</p>
          </div>
        </div>
      </div>

      <!-- 返回首頁 -->
      <div class="text-center mt-6">
        <NuxtLink to="/" class="text-sm text-gray-600 hover:text-primary-600 transition-colors">
          返回首頁
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bg-primary-50 { background-color: rgba(63, 124, 106, 0.05); }
.bg-primary-100 { background-color: rgba(63, 124, 106, 0.1); }
.text-primary-600 { color: #3F7C6A; }
.bg-primary-600 { background-color: #3F7C6A; }
.hover\:bg-primary-700:hover { background-color: #356957; }
.focus\:ring-primary-500:focus { --tw-ring-color: rgba(63, 124, 106, 0.5); }
.focus\:border-primary-500:focus { border-color: #3F7C6A; }
.hover\:text-primary-600:hover { color: #3F7C6A; }
</style>
