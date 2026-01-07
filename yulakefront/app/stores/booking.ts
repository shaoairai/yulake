/**
 * 預約流程狀態管理
 * 使用 Pinia 管理預約流程中的選擇狀態
 * 支援 sessionStorage 持久化，避免登入後遺失資料
 */
import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import type { SalonPublicInfo, ServiceItem, StylistInfo } from '~/composables/useBookingApi'

const STORAGE_KEY = 'yulake_booking_state'

// 從 sessionStorage 讀取
const loadFromStorage = () => {
  if (typeof window === 'undefined') return null
  try {
    const stored = sessionStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : null
  } catch {
    return null
  }
}

// 儲存到 sessionStorage
const saveToStorage = (state: Record<string, unknown>) => {
  if (typeof window === 'undefined') return
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } catch {
    // 忽略儲存錯誤
  }
}

export const useBookingStore = defineStore('booking', () => {
  // 嘗試從 storage 恢復狀態
  const stored = loadFromStorage()

  // 店家資訊
  const salon = ref<SalonPublicInfo | null>(stored?.salon || null)

  // 選擇的服務
  const selectedService = ref<ServiceItem | null>(stored?.selectedService || null)

  // 選擇的設計師
  const selectedStylist = ref<StylistInfo | null>(stored?.selectedStylist || null)

  // 選擇的日期
  const selectedDate = ref(stored?.selectedDate || '')

  // 選擇的時間
  const selectedTime = ref(stored?.selectedTime || '')

  // 顧客備註
  const customerNote = ref(stored?.customerNote || '')

  // 計算屬性：是否可以選擇設計師
  const canSelectStylist = computed(() => {
    return !!selectedService.value
  })

  // 計算屬性：是否可以選擇時間
  const canSelectTime = computed(() => {
    return !!selectedService.value && !!selectedStylist.value
  })

  // 計算屬性：是否可以確認預約
  const canConfirm = computed(() => {
    return !!selectedService.value &&
      !!selectedStylist.value &&
      !!selectedDate.value &&
      !!selectedTime.value
  })

  // 計算屬性：預約摘要
  const bookingSummary = computed(() => {
    if (!canConfirm.value) return null

    return {
      salon: salon.value,
      service: selectedService.value,
      stylist: selectedStylist.value,
      date: selectedDate.value,
      time: selectedTime.value,
      note: customerNote.value
    }
  })

  // 設定店家
  const setSalon = (salonInfo: SalonPublicInfo) => {
    salon.value = salonInfo
  }

  // 選擇服務
  const selectService = (service: ServiceItem) => {
    selectedService.value = service
    // 清除後續選擇
    selectedStylist.value = null
    selectedDate.value = ''
    selectedTime.value = ''
  }

  // 選擇設計師
  const selectStylist = (stylist: StylistInfo) => {
    selectedStylist.value = stylist
    // 清除後續選擇
    selectedDate.value = ''
    selectedTime.value = ''
  }

  // 選擇日期時間
  const selectDateTime = (date: string, time: string) => {
    selectedDate.value = date
    selectedTime.value = time
  }

  // 設定備註
  const setNote = (note: string) => {
    customerNote.value = note
  }

  // 重置選擇（保留店家資訊）
  const reset = () => {
    selectedService.value = null
    selectedStylist.value = null
    selectedDate.value = ''
    selectedTime.value = ''
    customerNote.value = ''
  }

  // 完全清除
  const clearAll = () => {
    salon.value = null
    reset()
    clearStorage()
  }

  // 持久化狀態到 sessionStorage
  const persistState = () => {
    saveToStorage({
      salon: salon.value,
      selectedService: selectedService.value,
      selectedStylist: selectedStylist.value,
      selectedDate: selectedDate.value,
      selectedTime: selectedTime.value,
      customerNote: customerNote.value
    })
  }

  // 監聽所有狀態變化並自動持久化
  watch(
    [salon, selectedService, selectedStylist, selectedDate, selectedTime, customerNote],
    () => {
      persistState()
    },
    { deep: true }
  )

  // 清除持久化資料
  const clearStorage = () => {
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem(STORAGE_KEY)
    }
  }

  return {
    // 狀態
    salon,
    selectedService,
    selectedStylist,
    selectedDate,
    selectedTime,
    customerNote,

    // 計算屬性
    canSelectStylist,
    canSelectTime,
    canConfirm,
    bookingSummary,

    // 方法
    setSalon,
    selectService,
    selectStylist,
    selectDateTime,
    setNote,
    reset,
    clearAll,
    clearStorage
  }
})
