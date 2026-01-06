/**
 * useBookingApi - 預約相關 API
 * 處理顧客端的預約功能
 */
import { useApi } from './useApi'

// 店家資訊
export interface SalonPublicInfo {
  id: string
  code: string
  name: string
  address: string
  phone: string
  line_id?: string
  ig_account?: string
  website?: string
  logo_url?: string
  theme_color: string
  booking_url: string
  business_hours: BusinessHour[]
  booking_rule?: BookingRule
}

// 營業時間
export interface BusinessHour {
  day_of_week: number
  is_open: boolean
  open_time: string | null
  close_time: string | null
}

// 預約規則
export interface BookingRule {
  slot_interval: number
  min_advance_hours: number
  max_advance_days: number
  require_confirmation: boolean
}

// 服務項目
export interface ServiceItem {
  id: string
  name: string
  description?: string
  duration: number
  price: number
  image_url?: string
}

// 設計師
export interface StylistInfo {
  id: string
  name: string
  style?: string
  introduction?: string
  avatar_url?: string
}

// 可用時段
export interface TimeSlot {
  start_time: string
  end_time: string
}

// 預約資訊
export interface BookingInfo {
  id: string
  salon: {
    id: string
    code: string
    name: string
    address: string
    phone: string
    theme_color?: string
  }
  service: {
    id: string
    name: string
    description?: string
    duration: number
    price: number
  }
  stylist: {
    id: string
    name: string
    avatar_url?: string
  }
  booking_date: string
  start_time: string
  end_time: string
  status: string
  customer_note?: string
  cancelled_at?: string
  cancel_reason?: string
  created_at: string
}

export function useBookingApi() {
  const api = useApi()

  // ===== 公開 API（不需登入）=====

  // 取得店家資訊
  const getSalonInfo = async (code: string) => {
    return api.get<SalonPublicInfo>(`/api/salons/${code}`, undefined, { includeAuth: false })
  }

  // 取得服務列表
  const getServices = async (code: string) => {
    return api.get<ServiceItem[]>(`/api/salons/${code}/services`, undefined, { includeAuth: false })
  }

  // 取得設計師列表
  const getStylists = async (code: string, serviceId?: string) => {
    return api.get<StylistInfo[]>(
      `/api/salons/${code}/stylists`,
      serviceId ? { service_id: serviceId } : undefined,
      { includeAuth: false }
    )
  }

  // 取得可用時段
  const getAvailableSlots = async (
    code: string,
    stylistId: string,
    serviceId: string,
    date: string
  ) => {
    return api.get<{
      date: string
      stylist: { id: string; name: string }
      service: { id: string; name: string; duration: number }
      slots: TimeSlot[]
    }>(`/api/salons/${code}/available-slots`, {
      stylist_id: stylistId,
      service_id: serviceId,
      date
    }, { includeAuth: false })
  }

  // ===== 需要登入的 API =====

  // 建立預約
  const createBooking = async (data: {
    salon_code: string
    service_id: string
    stylist_id: string
    booking_date: string
    start_time: string
    customer_note?: string
  }) => {
    return api.post<BookingInfo>('/api/bookings', data)
  }

  // 取得我的預約列表
  const getMyBookings = async (status?: string, page: number = 1, perPage: number = 20) => {
    return api.get<BookingInfo[]>('/api/me/bookings', { status, page, per_page: perPage })
  }

  // 取得預約詳情
  const getMyBookingDetail = async (bookingId: string) => {
    return api.get<BookingInfo>(`/api/me/bookings/${bookingId}`)
  }

  // 取消預約
  const cancelMyBooking = async (bookingId: string, reason?: string) => {
    return api.put<{ id: string; status: string; cancelled_at: string }>(
      `/api/me/bookings/${bookingId}/cancel`,
      { reason }
    )
  }

  // 取得個人資料
  const getMyProfile = async () => {
    return api.get<{
      id: string
      name: string
      email: string
      phone?: string
      birthday?: string
      created_at: string
    }>('/api/me/profile')
  }

  // 更新個人資料
  const updateMyProfile = async (data: {
    name?: string
    phone?: string
    birthday?: string | null
  }) => {
    return api.put<{
      id: string
      name: string
      phone?: string
      birthday?: string
    }>('/api/me/profile', data)
  }

  return {
    // 公開 API
    getSalonInfo,
    getServices,
    getStylists,
    getAvailableSlots,

    // 需登入 API
    createBooking,
    getMyBookings,
    getMyBookingDetail,
    cancelMyBooking,
    getMyProfile,
    updateMyProfile
  }
}
