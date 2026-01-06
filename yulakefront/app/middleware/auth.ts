/**
 * 認證中介層
 * 保護需要登入的路由
 */
export default defineNuxtRouteMiddleware((to) => {
  // 僅在客戶端執行
  if (import.meta.server) return

  const token = localStorage.getItem('auth_token')

  // 檢查是否需要認證
  const requiresAuth = to.path.startsWith('/admin') && to.path !== '/admin/login'

  if (requiresAuth && !token) {
    // 未登入，導向登入頁
    return navigateTo('/admin/login')
  }

  // 已登入但訪問登入頁，導向後台首頁
  if (to.path === '/admin/login' && token) {
    return navigateTo('/admin')
  }
})
