<script setup lang="ts">
/**
 * 首頁 - 客戶直接進入預約流程
 * 輸入店家代碼後直接開始預約
 */

const salonCode = ref('')
const isLoading = ref(false)
const errorMessage = ref('')

const handleStartBooking = async () => {
  if (!salonCode.value.trim()) {
    errorMessage.value = '請輸入店家代碼'
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  // 直接導向該店家的預約頁面
  await navigateTo(`/s/${salonCode.value.trim()}/booking`)
}

// 按 Enter 鍵也可以開始預約
const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter') {
    handleStartBooking()
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-pink-50 via-white to-purple-50">
    <!-- 主內容區 -->
    <div class="flex flex-col items-center justify-center min-h-screen px-4">
      <!-- Logo 和標題 -->
      <div class="text-center mb-8">
        <div class="w-20 h-20 bg-gradient-to-br from-pink-400 to-purple-500 rounded-full mx-auto mb-4 flex items-center justify-center shadow-lg">
          <span class="text-3xl text-white">💅</span>
        </div>
        <h1 class="text-3xl font-bold text-gray-800 mb-2">Yulake</h1>
        <p class="text-gray-500">美甲美睫預約平台</p>
      </div>

      <!-- 預約卡片 -->
      <div class="w-full max-w-md bg-white rounded-2xl shadow-xl p-8">
        <h2 class="text-xl font-semibold text-gray-800 text-center mb-6">
          開始預約
        </h2>

        <!-- 輸入店家代碼 -->
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              店家代碼
            </label>
            <input
              v-model="salonCode"
              type="text"
              placeholder="請輸入店家代碼，例如：nailart"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-pink-300 focus:border-pink-400 transition-all text-center text-lg"
              :disabled="isLoading"
              @keydown="handleKeydown"
            >
          </div>

          <!-- 錯誤訊息 -->
          <p v-if="errorMessage" class="text-red-500 text-sm text-center">
            {{ errorMessage }}
          </p>

          <!-- 開始預約按鈕 -->
          <button
            class="w-full mt-2 px-6 py-4 bg-gradient-to-r from-pink-500 to-purple-600 text-white text-lg font-semibold rounded-xl shadow-lg hover:shadow-xl hover:from-pink-600 hover:to-purple-700 active:scale-[0.98] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="isLoading"
            @click="handleStartBooking"
          >
            <span v-if="isLoading" class="inline-flex items-center justify-center gap-2">
              <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              載入中...
            </span>
            <span v-else>開始預約</span>
          </button>
        </div>

        <!-- 分隔線 -->
        <div class="flex items-center my-6">
          <div class="flex-1 border-t border-gray-200"></div>
          <span class="px-4 text-sm text-gray-400">或</span>
          <div class="flex-1 border-t border-gray-200"></div>
        </div>

        <!-- 快速連結 -->
        <div class="space-y-3">
          <p class="text-sm text-gray-500 text-center mb-3">
            已經有帳號？
          </p>
          <NuxtLink
            to="/auth/login"
            class="block w-full py-3 border border-gray-200 text-gray-700 font-medium rounded-xl hover:bg-gray-50 transition-all text-center"
          >
            登入查看我的預約
          </NuxtLink>
        </div>
      </div>

      <!-- 底部連結 -->
      <div class="mt-8 text-center">
        <p class="text-sm text-gray-400 mb-2">是店家嗎？</p>
        <NuxtLink
          to="/portal"
          class="text-pink-500 hover:text-pink-600 font-medium text-sm"
        >
          前往店家入口
        </NuxtLink>
      </div>
    </div>
  </div>
</template>
