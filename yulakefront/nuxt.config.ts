// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  // 模組
  modules: ['@nuxt/eslint', '@nuxt/image'],

  // 全域 CSS
  css: ['~/assets/css/main.css'],

  // 元件設定 - 移除路徑前綴讓元件可直接使用原名稱
  components: [
    { path: '~/components/ui', prefix: '' },
    { path: '~/components/admin', prefix: 'Admin' },
    { path: '~/components', pathPrefix: false }
  ],

  // 執行時設定
  runtimeConfig: {
    public: {
      apiUrl: process.env.NUXT_PUBLIC_API_URL || 'http://localhost:5000'
    }
  },

  // Vite 設定
  vite: {
    server: {
      watch: {
        usePolling: true,
        interval: 300
      }
    }
  }
})