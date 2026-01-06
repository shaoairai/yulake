/**
 * useAuth - 認證狀態管理
 * 處理店家與顧客的登入/登出/認證狀態
 */
import { ref, computed } from 'vue'
import { useApi, ApiError } from './useApi'

// 使用者類型
export type UserType = 'salon' | 'customer' | null

// 店家使用者資訊
export interface SalonUser {
  id: string
  name: string
  email: string
  role: 'owner' | 'staff'
}

// 店家資訊
export interface SalonInfo {
  id: string
  code: string
  name: string
}

// 顧客使用者資訊
export interface CustomerUser {
  id: string
  name: string
  email: string
  phone?: string
}

// 認證狀態
interface AuthState {
  isAuthenticated: boolean
  userType: UserType
  salonUser: SalonUser | null
  salonInfo: SalonInfo | null
  customerUser: CustomerUser | null
  loading: boolean
  error: string | null
}

// 全域認證狀態
const authState = ref<AuthState>({
  isAuthenticated: false,
  userType: null,
  salonUser: null,
  salonInfo: null,
  customerUser: null,
  loading: false,
  error: null
})

export function useAuth() {
  const api = useApi()

  // 計算屬性
  const isAuthenticated = computed(() => authState.value.isAuthenticated)
  const userType = computed(() => authState.value.userType)
  const salonUser = computed(() => authState.value.salonUser)
  const salonInfo = computed(() => authState.value.salonInfo)
  const customerUser = computed(() => authState.value.customerUser)
  const loading = computed(() => authState.value.loading)
  const error = computed(() => authState.value.error)

  // 店家登入
  const salonLogin = async (email: string, password: string): Promise<boolean> => {
    authState.value.loading = true
    authState.value.error = null

    try {
      const response = await api.post<{
        token: string
        user: SalonUser
        salon: SalonInfo
      }>('/api/auth/salon/login', { email, password }, { includeAuth: false })

      if (response.success && response.data) {
        api.setToken(response.data.token)
        authState.value.isAuthenticated = true
        authState.value.userType = 'salon'
        authState.value.salonUser = response.data.user
        authState.value.salonInfo = response.data.salon
        return true
      }
      return false
    } catch (err) {
      if (err instanceof ApiError) {
        authState.value.error = err.message
      } else {
        authState.value.error = '登入失敗，請稍後再試'
      }
      return false
    } finally {
      authState.value.loading = false
    }
  }

  // 顧客登入
  const customerLogin = async (email: string, password: string): Promise<boolean> => {
    authState.value.loading = true
    authState.value.error = null

    try {
      const response = await api.post<{
        token: string
        user: CustomerUser
      }>('/api/auth/customer/login', { email, password }, { includeAuth: false })

      if (response.success && response.data) {
        api.setToken(response.data.token)
        authState.value.isAuthenticated = true
        authState.value.userType = 'customer'
        authState.value.customerUser = response.data.user
        return true
      }
      return false
    } catch (err) {
      if (err instanceof ApiError) {
        authState.value.error = err.message
      } else {
        authState.value.error = '登入失敗，請稍後再試'
      }
      return false
    } finally {
      authState.value.loading = false
    }
  }

  // 顧客註冊
  const customerRegister = async (
    name: string,
    email: string,
    password: string,
    phone?: string
  ): Promise<boolean> => {
    authState.value.loading = true
    authState.value.error = null

    try {
      const response = await api.post<{
        token: string
        user: CustomerUser
      }>('/api/auth/customer/register', { name, email, password, phone }, { includeAuth: false })

      if (response.success && response.data) {
        api.setToken(response.data.token)
        authState.value.isAuthenticated = true
        authState.value.userType = 'customer'
        authState.value.customerUser = response.data.user
        return true
      }
      return false
    } catch (err) {
      if (err instanceof ApiError) {
        authState.value.error = err.message
      } else {
        authState.value.error = '註冊失敗，請稍後再試'
      }
      return false
    } finally {
      authState.value.loading = false
    }
  }

  // 驗證 Token 並取得使用者資訊
  const checkAuth = async (): Promise<boolean> => {
    const token = api.getToken()
    if (!token) {
      resetAuth()
      return false
    }

    authState.value.loading = true

    try {
      // 先嘗試店家身份
      try {
        const salonResponse = await api.get<{
          user: SalonUser
          salon: SalonInfo
        }>('/api/auth/salon/me')

        if (salonResponse.success && salonResponse.data) {
          authState.value.isAuthenticated = true
          authState.value.userType = 'salon'
          authState.value.salonUser = salonResponse.data.user
          authState.value.salonInfo = salonResponse.data.salon
          return true
        }
      } catch {
        // 不是店家 Token，嘗試顧客
      }

      // 嘗試顧客身份
      try {
        const customerResponse = await api.get<CustomerUser>('/api/auth/customer/me')

        if (customerResponse.success && customerResponse.data) {
          authState.value.isAuthenticated = true
          authState.value.userType = 'customer'
          authState.value.customerUser = customerResponse.data
          return true
        }
      } catch {
        // 也不是顧客 Token
      }

      // Token 無效
      resetAuth()
      return false
    } catch {
      resetAuth()
      return false
    } finally {
      authState.value.loading = false
    }
  }

  // 登出
  const logout = () => {
    api.clearToken()
    resetAuth()
  }

  // 重設認證狀態
  const resetAuth = () => {
    authState.value.isAuthenticated = false
    authState.value.userType = null
    authState.value.salonUser = null
    authState.value.salonInfo = null
    authState.value.customerUser = null
    authState.value.error = null
  }

  // 清除錯誤
  const clearError = () => {
    authState.value.error = null
  }

  return {
    // 狀態
    isAuthenticated,
    userType,
    salonUser,
    salonInfo,
    customerUser,
    loading,
    error,

    // 方法
    salonLogin,
    customerLogin,
    customerRegister,
    checkAuth,
    logout,
    clearError
  }
}
