/**
 * useAdminApi - 店家後台 API
 * 處理店家後台所有功能的 API 呼叫
 */
import { useApi } from './useApi'

// ===== 型別定義 =====

// 預約狀態
export type BookingStatus =
  | 'pending'
  | 'confirmed'
  | 'completed'
  | 'cancelled_by_customer'
  | 'cancelled_by_salon'
  | 'no_show'

// 預約資訊
export interface AdminBooking {
  id: string
  customer: {
    id: string
    name: string
    phone?: string
  }
  service: {
    id: string
    name: string
    duration: number
    price: number
  }
  stylist: {
    id: string
    name: string
  }
  booking_date: string
  start_time: string
  end_time: string
  status: BookingStatus
  customer_note?: string
  salon_note?: string
  created_at: string
}

// 顧客資訊
export interface AdminCustomer {
  id: string
  name: string
  email: string
  phone?: string
  stats?: {
    total_bookings: number
    completed_bookings: number
    no_show_count: number
    total_spent: number
  }
  salon_relation?: {
    note?: string
    is_blacklisted: boolean
    blacklist_reason?: string
    first_visit_at?: string
    last_visit_at?: string
  }
  tier?: {
    id: string
    name: string
    color: string
  }
  created_at: string
}

// 服務項目
export interface AdminService {
  id: string
  name: string
  description?: string
  duration: number
  price: number
  image_url?: string
  sort_order: number
  is_active: boolean
}

// 設計師
export interface AdminStylist {
  id: string
  name: string
  style?: string
  introduction?: string
  avatar_url?: string
  sort_order: number
  is_active: boolean
  services?: string[]
}

// 店家設定
export interface SalonSettings {
  salon: {
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
  }
  business_hours: {
    day_of_week: number
    is_open: boolean
    open_time: string | null
    close_time: string | null
  }[]
  booking_rule: {
    slot_interval: number
    min_advance_hours: number
    max_advance_days: number
    require_confirmation: boolean
  }
}

// 特殊日期
export interface SpecialDate {
  id: string
  date: string
  type: 'closed' | 'special_hours'
  open_time?: string
  close_time?: string
  reason?: string
}

// 儀表板統計
export interface DashboardStats {
  today_bookings: number
  pending_bookings: number
  week_bookings: number
  month_revenue: number
  recent_bookings: AdminBooking[]
}

// 會員等級
export interface MembershipTier {
  id: string
  name: string
  level: number
  min_points: number
  min_spent: number
  min_visits: number
  discount_percent: number
  benefits?: string
  color: string
  sort_order: number
  is_active: boolean
  member_count?: number
}

// 集點規則
export interface PointRule {
  points_per_visit: number
  points_per_amount: number
  bonus_birthday_points: number
  upgrade_rule_type: 'points' | 'spent' | 'visits' | 'combined'
  points_expiry_months: number
  is_active: boolean
}

export function useAdminApi() {
  const api = useApi()

  // ===== 儀表板 =====
  const getDashboard = async () => {
    return api.get<DashboardStats>('/api/salon/dashboard')
  }

  // ===== 預約管理 =====
  const getBookings = async (params?: {
    status?: string
    date?: string
    stylist_id?: string
    page?: number
    per_page?: number
  }) => {
    return api.get<AdminBooking[]>('/api/salon/bookings', params)
  }

  const getBookingDetail = async (bookingId: string) => {
    return api.get<AdminBooking>(`/api/salon/bookings/${bookingId}`)
  }

  const updateBookingStatus = async (bookingId: string, status: BookingStatus, note?: string) => {
    return api.put<AdminBooking>(`/api/salon/bookings/${bookingId}/status`, { status, note })
  }

  const getCalendarData = async (startDate: string, endDate: string, stylistId?: string) => {
    return api.get<AdminBooking[]>('/api/salon/calendar', {
      start_date: startDate,
      end_date: endDate,
      stylist_id: stylistId
    })
  }

  // ===== 顧客管理 =====
  const getCustomers = async (params?: {
    search?: string
    is_blacklisted?: boolean
    page?: number
    per_page?: number
  }) => {
    return api.get<AdminCustomer[]>('/api/salon/customers', params)
  }

  const getCustomerDetail = async (customerId: string) => {
    return api.get<AdminCustomer>(`/api/salon/customers/${customerId}`)
  }

  const updateCustomerNote = async (customerId: string, note: string) => {
    return api.put<{ note: string }>(`/api/salon/customers/${customerId}/note`, { note })
  }

  const addToBlacklist = async (customerId: string, reason: string) => {
    return api.post(`/api/salon/customers/${customerId}/blacklist`, { reason })
  }

  const removeFromBlacklist = async (customerId: string) => {
    return api.del(`/api/salon/customers/${customerId}/blacklist`)
  }

  // ===== 服務管理 =====
  const getServices = async () => {
    return api.get<AdminService[]>('/api/salon/services')
  }

  const createService = async (data: Omit<AdminService, 'id'>) => {
    return api.post<AdminService>('/api/salon/services', data as Record<string, unknown>)
  }

  const updateService = async (serviceId: string, data: Partial<AdminService>) => {
    return api.put<AdminService>(`/api/salon/services/${serviceId}`, data as Record<string, unknown>)
  }

  const deleteService = async (serviceId: string) => {
    return api.del(`/api/salon/services/${serviceId}`)
  }

  // ===== 設計師管理 =====
  const getStylists = async () => {
    return api.get<AdminStylist[]>('/api/salon/stylists')
  }

  const createStylist = async (data: Omit<AdminStylist, 'id'>) => {
    return api.post<AdminStylist>('/api/salon/stylists', data as Record<string, unknown>)
  }

  const updateStylist = async (stylistId: string, data: Partial<AdminStylist>) => {
    return api.put<AdminStylist>(`/api/salon/stylists/${stylistId}`, data as Record<string, unknown>)
  }

  const deleteStylist = async (stylistId: string) => {
    return api.del(`/api/salon/stylists/${stylistId}`)
  }

  // ===== 店家設定 =====
  const getSettings = async () => {
    return api.get<SalonSettings>('/api/salon/settings')
  }

  const updateSettings = async (data: Partial<SalonSettings['salon']>) => {
    return api.put('/api/salon/settings', data as Record<string, unknown>)
  }

  const updateBusinessHours = async (hours: SalonSettings['business_hours']) => {
    return api.put('/api/salon/settings/hours', { business_hours: hours })
  }

  const updateBookingRules = async (rules: Partial<SalonSettings['booking_rule']>) => {
    return api.put('/api/salon/settings/rules', rules as Record<string, unknown>)
  }

  // ===== 特殊日期 =====
  const getSpecialDates = async (startDate?: string, endDate?: string) => {
    return api.get<SpecialDate[]>('/api/salon/special-dates', {
      start_date: startDate,
      end_date: endDate
    })
  }

  const createSpecialDate = async (data: Omit<SpecialDate, 'id'>) => {
    return api.post<SpecialDate>('/api/salon/special-dates', data as Record<string, unknown>)
  }

  const updateSpecialDate = async (dateId: string, data: Partial<SpecialDate>) => {
    return api.put<SpecialDate>(`/api/salon/special-dates/${dateId}`, data as Record<string, unknown>)
  }

  const deleteSpecialDate = async (dateId: string) => {
    return api.del(`/api/salon/special-dates/${dateId}`)
  }

  // ===== 會員等級 =====
  const getMembershipTiers = async () => {
    return api.get<MembershipTier[]>('/api/salon/membership/tiers')
  }

  const createMembershipTier = async (data: Omit<MembershipTier, 'id' | 'member_count'>) => {
    return api.post<MembershipTier>('/api/salon/membership/tiers', data as Record<string, unknown>)
  }

  const updateMembershipTier = async (tierId: string, data: Partial<MembershipTier>) => {
    return api.put<MembershipTier>(`/api/salon/membership/tiers/${tierId}`, data as Record<string, unknown>)
  }

  const deleteMembershipTier = async (tierId: string) => {
    return api.del(`/api/salon/membership/tiers/${tierId}`)
  }

  const setCustomerTier = async (customerId: string, tierId: string, expiresAt?: string) => {
    return api.put(`/api/salon/membership/customers/${customerId}/tier`, {
      tier_id: tierId,
      expires_at: expiresAt
    })
  }

  // ===== 集點規則 =====
  const getPointRules = async () => {
    return api.get<PointRule>('/api/salon/membership/point-rules')
  }

  const updatePointRules = async (rules: Partial<PointRule>) => {
    return api.put<PointRule>('/api/salon/membership/point-rules', rules as Record<string, unknown>)
  }

  const getCustomerPoints = async (customerId: string) => {
    return api.get<{
      customer_id: string
      total_points: number
      lifetime_points: number
      used_points: number
    }>(`/api/salon/membership/customers/${customerId}/points`)
  }

  const adjustCustomerPoints = async (customerId: string, points: number, description?: string) => {
    return api.post(`/api/salon/membership/customers/${customerId}/points`, { points, description })
  }

  const getMembershipStats = async () => {
    return api.get<{
      tier_stats: {
        tier_id: string
        tier_name: string
        level: number
        color: string
        member_count: number
      }[]
      total_with_tier: number
      total_without_tier: number
      total_customers: number
    }>('/api/salon/membership/stats')
  }

  // ===== Email 行銷 =====
  const getEmailTemplates = async (type?: string) => {
    return api.get('/api/salon/email/templates', { type })
  }

  const getEmailCampaigns = async (status?: string, page?: number, perPage?: number) => {
    return api.get('/api/salon/email/campaigns', { status, page, per_page: perPage })
  }

  const getAutoEmailRules = async () => {
    return api.get('/api/salon/email/auto-rules')
  }

  return {
    // 儀表板
    getDashboard,

    // 預約管理
    getBookings,
    getBookingDetail,
    updateBookingStatus,
    getCalendarData,

    // 顧客管理
    getCustomers,
    getCustomerDetail,
    updateCustomerNote,
    addToBlacklist,
    removeFromBlacklist,

    // 服務管理
    getServices,
    createService,
    updateService,
    deleteService,

    // 設計師管理
    getStylists,
    createStylist,
    updateStylist,
    deleteStylist,

    // 店家設定
    getSettings,
    updateSettings,
    updateBusinessHours,
    updateBookingRules,

    // 特殊日期
    getSpecialDates,
    createSpecialDate,
    updateSpecialDate,
    deleteSpecialDate,

    // 會員等級
    getMembershipTiers,
    createMembershipTier,
    updateMembershipTier,
    deleteMembershipTier,
    setCustomerTier,

    // 集點規則
    getPointRules,
    updatePointRules,
    getCustomerPoints,
    adjustCustomerPoints,
    getMembershipStats,

    // Email 行銷
    getEmailTemplates,
    getEmailCampaigns,
    getAutoEmailRules
  }
}
