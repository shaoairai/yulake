// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  // 模組
  modules: ['@nuxt/eslint', '@nuxt/image'],

  // 全域 CSS
  css: ['~/assets/css/main.css'],

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