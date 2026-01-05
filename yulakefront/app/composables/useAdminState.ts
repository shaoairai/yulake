/**
 * useAdminState - 廠商後台狀態管理
 * 管理篩選條件、UI 狀態等
 */
import { ref, reactive, computed } from 'vue'

// ========================================
// 型別定義
// ========================================

/** 日期範圍 */
export interface DateRange {
  startDate: string
  endDate: string
}

/** 預約篩選條件 */
export interface BookingFilters {
  dateRange: DateRange
  stylistId: string
  status: string
}

/** 當前店家管理者 */
export interface CurrentSalonOwner {
  id: string
  name: string
  email: string
  salonId: string
}

// ========================================
// 初始值
// ========================================

// 取得今天與一週後的日期
const today = new Date()
const oneWeekLater = new Date(today)
oneWeekLater.setDate(today.getDate() + 7)

const formatDate = (date: Date): string => {
  return date.toISOString().split('T')[0]
}

// ========================================
// Composable 函式
// ========================================

export function useAdminState() {
  // 當前店家管理者（假設已登入）
  const currentSalonOwner = reactive<CurrentSalonOwner>({
    id: 'owner_001',
    name: '王小姐',
    email: 'wang@wuguang-nails.com',
    salonId: 'salon_001'
  })

  // 預約篩選條件
  const bookingFilters = reactive<BookingFilters>({
    dateRange: {
      startDate: formatDate(today),
      endDate: formatDate(oneWeekLater)
    },
    stylistId: '',
    status: ''
  })

  // 顧客搜尋關鍵字
  const customerSearchKeyword = ref('')

  // 是否只顯示黑名單顧客
  const showBlacklistOnly = ref(false)

  // 當前開啟的 Modal
  const currentModal = ref<string | null>(null)

  // 側邊欄是否展開（行動版）
  const isSidebarOpen = ref(false)

  // ========================================
  // 計算屬性
  // ========================================

  // 是否有套用任何預約篩選條件
  const hasBookingFilters = computed(() => {
    return bookingFilters.stylistId !== '' || bookingFilters.status !== ''
  })

  // ========================================
  // 方法
  // ========================================

  /** 重置預約篩選條件 */
  const resetBookingFilters = () => {
    bookingFilters.dateRange = {
      startDate: formatDate(today),
      endDate: formatDate(oneWeekLater)
    }
    bookingFilters.stylistId = ''
    bookingFilters.status = ''
  }

  /** 更新預約日期範圍 */
  const setBookingDateRange = (startDate: string, endDate: string) => {
    bookingFilters.dateRange.startDate = startDate
    bookingFilters.dateRange.endDate = endDate
  }

  /** 更新設計師篩選 */
  const setBookingStylistFilter = (stylistId: string) => {
    bookingFilters.stylistId = stylistId
  }

  /** 更新狀態篩選 */
  const setBookingStatusFilter = (status: string) => {
    bookingFilters.status = status
  }

  /** 重置顧客搜尋 */
  const resetCustomerSearch = () => {
    customerSearchKeyword.value = ''
    showBlacklistOnly.value = false
  }

  /** 開啟 Modal */
  const openModal = (modalName: string) => {
    currentModal.value = modalName
  }

  /** 關閉 Modal */
  const closeModal = () => {
    currentModal.value = null
  }

  /** 切換側邊欄 */
  const toggleSidebar = () => {
    isSidebarOpen.value = !isSidebarOpen.value
  }

  /** 關閉側邊欄 */
  const closeSidebar = () => {
    isSidebarOpen.value = false
  }

  return {
    // 狀態
    currentSalonOwner,
    bookingFilters,
    customerSearchKeyword,
    showBlacklistOnly,
    currentModal,
    isSidebarOpen,

    // 計算屬性
    hasBookingFilters,

    // 方法
    resetBookingFilters,
    setBookingDateRange,
    setBookingStylistFilter,
    setBookingStatusFilter,
    resetCustomerSearch,
    openModal,
    closeModal,
    toggleSidebar,
    closeSidebar
  }
}
