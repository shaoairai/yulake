/**
 * useAdminMockData - 廠商後台假資料管理
 * 提供所有後台頁面需要的 mock data
 */
import { reactive, computed } from 'vue'

// ========================================
// 型別定義
// ========================================

/** 店家資料 */
export interface Salon {
  id: string
  name: string
  code: string
  address: string
  phone: string
  lineId: string
  igAccount: string
  website: string
  bookingUrl: string
  businessHours: BusinessHour[]
}

/** 營業時間 */
export interface BusinessHour {
  day: string
  isOpen: boolean
  openTime: string
  closeTime: string
}

/** 設計師 */
export interface Stylist {
  id: string
  name: string
  style: string
  introduction: string
  isActive: boolean
}

/** 服務項目 */
export interface Service {
  id: string
  name: string
  description: string
  duration: number
  price: number
  isActive: boolean
  stylists: string // 適用設計師（簡化為文字）
}

/** 顧客 */
export interface Customer {
  id: string
  name: string
  phone: string
  totalBookings: number
  completedBookings: number
  noShowCount: number
  isBlacklisted: boolean
  createdAt: string
  lastVisit: string
  note: string
}

/** 預約狀態 */
export type BookingStatus =
  | 'pending'
  | 'confirmed'
  | 'completed'
  | 'cancelled_by_customer'
  | 'cancelled_by_salon'
  | 'no_show'

/** 預約 */
export interface Booking {
  id: string
  customerId: string
  customerName: string
  customerPhone: string
  serviceId: string
  serviceName: string
  stylistId: string
  stylistName: string
  date: string
  startTime: string
  endTime: string
  status: BookingStatus
  note: string
  createdAt: string
}

/** 提醒 */
export interface Reminder {
  id: string
  type: 'birthday' | 'revisit'
  customerId: string
  customerName: string
  date: string
}

/** 統計數據 */
export interface Stats {
  weeklyBookings: number
  weeklyBookingsChange: string
  noShowCount: number
  noShowCountChange: string
  newCustomers: number
  newCustomersChange: string
}

// ========================================
// 假資料
// ========================================

/** 店家資料 */
const salonData: Salon = {
  id: 'salon_001',
  name: '霧光美甲工作室',
  code: 'wuguang-nails',
  address: '台北市大安區忠孝東路四段 123 號 5 樓',
  phone: '02-2771-1234',
  lineId: '@wuguang_nails',
  igAccount: 'wuguang_nails',
  website: 'https://wuguang-nails.com',
  bookingUrl: 'https://booking.yulake.com/s/wuguang-nails',
  businessHours: [
    { day: '週一', isOpen: false, openTime: '', closeTime: '' },
    { day: '週二', isOpen: true, openTime: '10:00', closeTime: '20:00' },
    { day: '週三', isOpen: true, openTime: '10:00', closeTime: '20:00' },
    { day: '週四', isOpen: true, openTime: '10:00', closeTime: '20:00' },
    { day: '週五', isOpen: true, openTime: '10:00', closeTime: '21:00' },
    { day: '週六', isOpen: true, openTime: '10:00', closeTime: '21:00' },
    { day: '週日', isOpen: true, openTime: '12:00', closeTime: '18:00' }
  ]
}

/** 設計師列表 */
const stylistsData: Stylist[] = [
  {
    id: 'stylist_001',
    name: 'Amy',
    style: '日系清新、簡約法式',
    introduction: '擁有 5 年美甲經驗，擅長日系清新風格與簡約法式設計，細心且有耐心。',
    isActive: true
  },
  {
    id: 'stylist_002',
    name: 'Bella',
    style: '韓系時尚、暈染漸層',
    introduction: '專精韓系時尚風格，擅長暈染與漸層技術，作品多次獲得客戶好評。',
    isActive: true
  },
  {
    id: 'stylist_003',
    name: 'Cindy',
    style: '手繪設計、客製圖案',
    introduction: '美術系畢業，擅長手繪設計與客製化圖案，可依據客戶需求創作獨特款式。',
    isActive: true
  },
  {
    id: 'stylist_004',
    name: 'Diana',
    style: '經典款式、保養護理',
    introduction: '資深美甲師，專精經典款式與手足保養護理，技術穩定可靠。',
    isActive: false
  }
]

/** 服務項目列表 */
const servicesData: Service[] = [
  {
    id: 'service_001',
    name: '基礎手部凝膠',
    description: '單色凝膠上色，含基礎手部保養與修型',
    duration: 60,
    price: 800,
    isActive: true,
    stylists: '全部設計師'
  },
  {
    id: 'service_002',
    name: '光療美甲（設計款）',
    description: '含設計款式，可選日系/韓系/法式等風格',
    duration: 90,
    price: 1200,
    isActive: true,
    stylists: 'Amy / Bella / Cindy'
  },
  {
    id: 'service_003',
    name: '手繪設計款',
    description: '客製化手繪圖案，每指單獨設計',
    duration: 120,
    price: 1800,
    isActive: true,
    stylists: 'Cindy'
  },
  {
    id: 'service_004',
    name: '足部凝膠',
    description: '足部單色凝膠，含基礎足部保養',
    duration: 75,
    price: 900,
    isActive: true,
    stylists: '全部設計師'
  },
  {
    id: 'service_005',
    name: '手足保養（無上色）',
    description: '深層保養與修型，不含上色',
    duration: 45,
    price: 500,
    isActive: true,
    stylists: 'Diana'
  },
  {
    id: 'service_006',
    name: '卸甲服務',
    description: '安全卸除凝膠/光療',
    duration: 30,
    price: 300,
    isActive: true,
    stylists: '全部設計師'
  }
]

/** 顧客列表 */
const customersData: Customer[] = reactive([
  {
    id: 'customer_001',
    name: '王小姐',
    phone: '0912-345-678',
    totalBookings: 12,
    completedBookings: 11,
    noShowCount: 0,
    isBlacklisted: false,
    createdAt: '2024-03-15',
    lastVisit: '2024-12-28',
    note: '喜歡日系簡約風格，對乳白色系情有獨鍾'
  },
  {
    id: 'customer_002',
    name: '李小姐',
    phone: '0923-456-789',
    totalBookings: 8,
    completedBookings: 7,
    noShowCount: 1,
    isBlacklisted: false,
    createdAt: '2024-05-20',
    lastVisit: '2024-12-20',
    note: '偏好韓系時尚款，喜歡嘗試新設計'
  },
  {
    id: 'customer_003',
    name: '陳小姐',
    phone: '0934-567-890',
    totalBookings: 5,
    completedBookings: 3,
    noShowCount: 2,
    isBlacklisted: true,
    createdAt: '2024-07-10',
    lastVisit: '2024-11-15',
    note: '已加入黑名單：連續兩次未出席且無法聯繫'
  },
  {
    id: 'customer_004',
    name: '林小姐',
    phone: '0945-678-901',
    totalBookings: 15,
    completedBookings: 15,
    noShowCount: 0,
    isBlacklisted: false,
    createdAt: '2024-01-05',
    lastVisit: '2025-01-02',
    note: 'VIP 顧客，固定每月回訪，喜歡經典法式'
  },
  {
    id: 'customer_005',
    name: '張小姐',
    phone: '0956-789-012',
    totalBookings: 3,
    completedBookings: 3,
    noShowCount: 0,
    isBlacklisted: false,
    createdAt: '2024-11-01',
    lastVisit: '2024-12-30',
    note: '新顧客，對手繪設計很有興趣'
  },
  {
    id: 'customer_006',
    name: '黃小姐',
    phone: '0967-890-123',
    totalBookings: 6,
    completedBookings: 6,
    noShowCount: 0,
    isBlacklisted: false,
    createdAt: '2024-08-15',
    lastVisit: '2024-12-25',
    note: '皮膚較敏感，需使用低敏產品'
  }
])

/** 預約列表 */
const bookingsData: Booking[] = reactive([
  // 今日預約
  {
    id: 'booking_001',
    customerId: 'customer_001',
    customerName: '王小姐',
    customerPhone: '0912-345-678',
    serviceId: 'service_002',
    serviceName: '光療美甲（設計款）',
    stylistId: 'stylist_001',
    stylistName: 'Amy',
    date: '2025-01-05',
    startTime: '10:00',
    endTime: '11:30',
    status: 'confirmed',
    note: '希望做淡粉色系的法式',
    createdAt: '2025-01-02 14:30'
  },
  {
    id: 'booking_002',
    customerId: 'customer_002',
    customerName: '李小姐',
    customerPhone: '0923-456-789',
    serviceId: 'service_002',
    serviceName: '光療美甲（設計款）',
    stylistId: 'stylist_002',
    stylistName: 'Bella',
    date: '2025-01-05',
    startTime: '14:00',
    endTime: '15:30',
    status: 'confirmed',
    note: '想要韓系暈染款',
    createdAt: '2025-01-03 09:15'
  },
  {
    id: 'booking_003',
    customerId: 'customer_004',
    customerName: '林小姐',
    customerPhone: '0945-678-901',
    serviceId: 'service_001',
    serviceName: '基礎手部凝膠',
    stylistId: 'stylist_001',
    stylistName: 'Amy',
    date: '2025-01-05',
    startTime: '16:00',
    endTime: '17:00',
    status: 'pending',
    note: '',
    createdAt: '2025-01-04 20:00'
  },
  // 其他預約
  {
    id: 'booking_004',
    customerId: 'customer_005',
    customerName: '張小姐',
    customerPhone: '0956-789-012',
    serviceId: 'service_003',
    serviceName: '手繪設計款',
    stylistId: 'stylist_003',
    stylistName: 'Cindy',
    date: '2025-01-06',
    startTime: '11:00',
    endTime: '13:00',
    status: 'confirmed',
    note: '想要客製化的花朵圖案',
    createdAt: '2025-01-01 16:45'
  },
  {
    id: 'booking_005',
    customerId: 'customer_006',
    customerName: '黃小姐',
    customerPhone: '0967-890-123',
    serviceId: 'service_004',
    serviceName: '足部凝膠',
    stylistId: 'stylist_002',
    stylistName: 'Bella',
    date: '2025-01-06',
    startTime: '15:00',
    endTime: '16:15',
    status: 'pending',
    note: '請使用低敏產品',
    createdAt: '2025-01-04 11:30'
  },
  // 過去預約
  {
    id: 'booking_006',
    customerId: 'customer_001',
    customerName: '王小姐',
    customerPhone: '0912-345-678',
    serviceId: 'service_002',
    serviceName: '光療美甲（設計款）',
    stylistId: 'stylist_001',
    stylistName: 'Amy',
    date: '2024-12-28',
    startTime: '14:00',
    endTime: '15:30',
    status: 'completed',
    note: '',
    createdAt: '2024-12-25 10:00'
  },
  {
    id: 'booking_007',
    customerId: 'customer_003',
    customerName: '陳小姐',
    customerPhone: '0934-567-890',
    serviceId: 'service_001',
    serviceName: '基礎手部凝膠',
    stylistId: 'stylist_002',
    stylistName: 'Bella',
    date: '2024-12-20',
    startTime: '11:00',
    endTime: '12:00',
    status: 'no_show',
    note: '未出席，電話未接',
    createdAt: '2024-12-18 15:20'
  },
  {
    id: 'booking_008',
    customerId: 'customer_002',
    customerName: '李小姐',
    customerPhone: '0923-456-789',
    serviceId: 'service_005',
    serviceName: '手足保養（無上色）',
    stylistId: 'stylist_004',
    stylistName: 'Diana',
    date: '2024-12-15',
    startTime: '16:00',
    endTime: '16:45',
    status: 'cancelled_by_customer',
    note: '顧客因故取消',
    createdAt: '2024-12-10 09:00'
  }
])

/** 提醒列表 */
const remindersData: Reminder[] = [
  {
    id: 'reminder_001',
    type: 'birthday',
    customerId: 'customer_001',
    customerName: '王小姐',
    date: '2025-01-10'
  },
  {
    id: 'reminder_002',
    type: 'revisit',
    customerId: 'customer_006',
    customerName: '黃小姐',
    date: '2025-01-08'
  },
  {
    id: 'reminder_003',
    type: 'revisit',
    customerId: 'customer_005',
    customerName: '張小姐',
    date: '2025-01-12'
  }
]

// ========================================
// Composable 函式
// ========================================

export function useAdminMockData() {
  // 店家資料
  const salon = reactive(salonData)

  // 設計師列表
  const stylists = reactive(stylistsData)

  // 服務項目列表
  const services = reactive(servicesData)

  // 顧客列表
  const customers = customersData

  // 預約列表
  const bookings = bookingsData

  // 提醒列表
  const reminders = reactive(remindersData)

  // 統計數據
  const stats = computed<Stats>(() => ({
    weeklyBookings: 24,
    weeklyBookingsChange: '+12%',
    noShowCount: 2,
    noShowCountChange: '-50%',
    newCustomers: 8,
    newCustomersChange: '+33%'
  }))

  // 今日預約（篩選今天日期的預約）
  const todayBookings = computed(() => {
    const today = '2025-01-05' // 模擬今日日期
    return bookings.filter(b => b.date === today)
  })

  // ========================================
  // 操作方法
  // ========================================

  /** 更新預約狀態 */
  const updateBookingStatus = (bookingId: string, newStatus: BookingStatus) => {
    const booking = bookings.find(b => b.id === bookingId)
    if (booking) {
      booking.status = newStatus

      // 如果標記為 no_show，更新顧客爽約次數
      if (newStatus === 'no_show') {
        const customer = customers.find(c => c.id === booking.customerId)
        if (customer) {
          customer.noShowCount += 1
        }
      }
    }
  }

  /** 切換顧客黑名單狀態 */
  const toggleCustomerBlacklist = (customerId: string) => {
    const customer = customers.find(c => c.id === customerId)
    if (customer) {
      customer.isBlacklisted = !customer.isBlacklisted
    }
  }

  /** 更新顧客備註 */
  const updateCustomerNote = (customerId: string, note: string) => {
    const customer = customers.find(c => c.id === customerId)
    if (customer) {
      customer.note = note
    }
  }

  /** 新增服務 */
  const addService = (service: Omit<Service, 'id'>) => {
    const newService: Service = {
      ...service,
      id: `service_${Date.now()}`
    }
    services.push(newService)
  }

  /** 更新服務 */
  const updateService = (serviceId: string, updates: Partial<Service>) => {
    const index = services.findIndex(s => s.id === serviceId)
    if (index !== -1) {
      Object.assign(services[index], updates)
    }
  }

  /** 新增設計師 */
  const addStylist = (stylist: Omit<Stylist, 'id'>) => {
    const newStylist: Stylist = {
      ...stylist,
      id: `stylist_${Date.now()}`
    }
    stylists.push(newStylist)
  }

  /** 更新設計師 */
  const updateStylist = (stylistId: string, updates: Partial<Stylist>) => {
    const index = stylists.findIndex(s => s.id === stylistId)
    if (index !== -1) {
      Object.assign(stylists[index], updates)
    }
  }

  /** 更新店家資料 */
  const updateSalon = (updates: Partial<Salon>) => {
    Object.assign(salon, updates)
  }

  return {
    // 資料
    salon,
    stylists,
    services,
    customers,
    bookings,
    reminders,
    stats,
    todayBookings,

    // 方法
    updateBookingStatus,
    toggleCustomerBlacklist,
    updateCustomerNote,
    addService,
    updateService,
    addStylist,
    updateStylist,
    updateSalon
  }
}
