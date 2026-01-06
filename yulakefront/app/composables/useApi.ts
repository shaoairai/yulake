/**
 * useApi - API 呼叫封裝
 * 統一處理 API 請求、Token 認證、錯誤處理
 */

// API 回應格式
export interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  message?: string
  error?: {
    code: string
    message: string
    details?: Record<string, unknown>
  }
  meta?: {
    pagination?: {
      page: number
      per_page: number
      total: number
      total_pages: number
      has_next: boolean
      has_prev: boolean
    }
  }
}

// API 錯誤
export class ApiError extends Error {
  code: string
  status: number
  details?: Record<string, unknown>

  constructor(code: string, message: string, status: number, details?: Record<string, unknown>) {
    super(message)
    this.code = code
    this.status = status
    this.details = details
  }
}

export function useApi() {
  // 取得 API URL
  const config = useRuntimeConfig()
  const API_BASE_URL = config.public.apiUrl as string || 'http://localhost:5000'
  // 取得 Token
  const getToken = (): string | null => {
    if (typeof window === 'undefined') return null
    return localStorage.getItem('auth_token')
  }

  // 設定 Token
  const setToken = (token: string) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token)
    }
  }

  // 清除 Token
  const clearToken = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token')
    }
  }

  // 建立請求標頭
  const buildHeaders = (includeAuth: boolean = true): HeadersInit => {
    const headers: HeadersInit = {
      'Content-Type': 'application/json'
    }

    if (includeAuth) {
      const token = getToken()
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
    }

    return headers
  }

  // 處理回應
  const handleResponse = async <T>(response: Response): Promise<ApiResponse<T>> => {
    const data = await response.json()

    if (!response.ok || !data.success) {
      const error = data.error || { code: 'UNKNOWN_ERROR', message: '未知錯誤' }
      throw new ApiError(error.code, error.message, response.status, error.details)
    }

    return data as ApiResponse<T>
  }

  // GET 請求
  const get = async <T>(
    endpoint: string,
    params?: Record<string, string | number | boolean | undefined>,
    options?: { includeAuth?: boolean }
  ): Promise<ApiResponse<T>> => {
    const url = new URL(`${API_BASE_URL}${endpoint}`)

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          url.searchParams.append(key, String(value))
        }
      })
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: buildHeaders(options?.includeAuth ?? true)
    })

    return handleResponse<T>(response)
  }

  // POST 請求
  const post = async <T>(
    endpoint: string,
    body?: Record<string, unknown>,
    options?: { includeAuth?: boolean }
  ): Promise<ApiResponse<T>> => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: buildHeaders(options?.includeAuth ?? true),
      body: body ? JSON.stringify(body) : undefined
    })

    return handleResponse<T>(response)
  }

  // PUT 請求
  const put = async <T>(
    endpoint: string,
    body?: Record<string, unknown>,
    options?: { includeAuth?: boolean }
  ): Promise<ApiResponse<T>> => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: buildHeaders(options?.includeAuth ?? true),
      body: body ? JSON.stringify(body) : undefined
    })

    return handleResponse<T>(response)
  }

  // DELETE 請求
  const del = async <T>(
    endpoint: string,
    options?: { includeAuth?: boolean }
  ): Promise<ApiResponse<T>> => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers: buildHeaders(options?.includeAuth ?? true)
    })

    return handleResponse<T>(response)
  }

  return {
    get,
    post,
    put,
    del,
    getToken,
    setToken,
    clearToken,
    API_BASE_URL
  }
}
