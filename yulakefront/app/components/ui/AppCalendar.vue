<template>
  <!-- 通用日曆元件 -->
  <div class="app-calendar">
    <!-- 日曆頭部 -->
    <div class="calendar-header">
      <div class="calendar-nav">
        <button class="nav-btn" @click="goToPreviousPeriod" :title="previousPeriodLabel">
          <span class="nav-icon">‹</span>
        </button>
        <button class="nav-btn today-btn" @click="goToToday">今日</button>
        <button class="nav-btn" @click="goToNextPeriod" :title="nextPeriodLabel">
          <span class="nav-icon">›</span>
        </button>
      </div>

      <h2 class="calendar-title">{{ currentPeriodTitle }}</h2>

      <div class="calendar-view-switcher">
        <button
          v-for="viewOption in viewOptions"
          :key="viewOption.value"
          :class="['view-btn', { active: view === viewOption.value }]"
          @click="setView(viewOption.value)"
        >
          {{ viewOption.label }}
        </button>
      </div>
    </div>

    <!-- 月視圖 -->
    <div v-if="view === 'month'" class="calendar-month">
      <!-- 星期標題 -->
      <div class="month-header">
        <div v-for="day in weekDays" :key="day" class="month-header-cell">
          {{ day }}
        </div>
      </div>
      <!-- 日期格子 -->
      <div class="month-grid">
        <div
          v-for="(day, index) in monthDays"
          :key="index"
          :class="[
            'month-cell',
            { 'other-month': !day.isCurrentMonth },
            { 'today': day.isToday },
            { 'selected': isDateSelected(day.date) }
          ]"
          @click="handleDateClick(day.date)"
        >
          <div class="cell-header">
            <span class="date-number">{{ day.dayNumber }}</span>
          </div>
          <div class="cell-events">
            <div
              v-for="event in getEventsForDate(day.date).slice(0, 3)"
              :key="event.id"
              :class="['event-item', `event-${event.status}`]"
              :title="`${event.startTime} ${event.customerName} - ${event.serviceName}`"
              @click.stop="handleEventClick(event)"
            >
              <span class="event-time">{{ event.startTime }}</span>
              <span class="event-title">{{ event.customerName }}</span>
            </div>
            <div
              v-if="getEventsForDate(day.date).length > 3"
              class="more-events"
              @click.stop="handleMoreClick(day.date)"
            >
              +{{ getEventsForDate(day.date).length - 3 }} 更多
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 週視圖 -->
    <div v-else-if="view === 'week'" class="calendar-week">
      <!-- 週標題 -->
      <div class="week-header">
        <div class="time-gutter"></div>
        <div
          v-for="day in weekViewDays"
          :key="day.date"
          :class="['week-header-cell', { 'today': day.isToday }]"
        >
          <span class="day-name">{{ day.dayName }}</span>
          <span class="day-number">{{ day.dayNumber }}</span>
        </div>
      </div>
      <!-- 時間格子 -->
      <div class="week-body">
        <div class="time-column">
          <div v-for="hour in hours" :key="hour" class="time-slot">
            {{ formatHour(hour) }}
          </div>
        </div>
        <div class="week-grid">
          <div
            v-for="day in weekViewDays"
            :key="day.date"
            :class="['week-column', { 'today': day.isToday }]"
          >
            <div v-for="hour in hours" :key="hour" class="hour-cell">
              <!-- 事件會在這裡絕對定位 -->
            </div>
            <!-- 事件區塊 -->
            <div
              v-for="event in getEventsForDate(day.date)"
              :key="event.id"
              :class="['week-event', `event-${event.status}`]"
              :style="getEventStyle(event)"
              @click="handleEventClick(event)"
            >
              <div class="event-content">
                <span class="event-time">{{ event.startTime }} - {{ event.endTime }}</span>
                <span class="event-title">{{ event.customerName }}</span>
                <span class="event-service">{{ event.serviceName }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 日視圖 -->
    <div v-else-if="view === 'day'" class="calendar-day">
      <div class="day-header">
        <span class="day-title">{{ dayViewTitle }}</span>
      </div>
      <div class="day-body">
        <div class="time-column">
          <div v-for="hour in hours" :key="hour" class="time-slot">
            {{ formatHour(hour) }}
          </div>
        </div>
        <div class="day-content">
          <div v-for="hour in hours" :key="hour" class="hour-cell"></div>
          <!-- 事件區塊 -->
          <div
            v-for="event in currentDayEvents"
            :key="event.id"
            :class="['day-event', `event-${event.status}`]"
            :style="getEventStyle(event)"
            @click="handleEventClick(event)"
          >
            <div class="event-content">
              <span class="event-time">{{ event.startTime }} - {{ event.endTime }}</span>
              <span class="event-title">{{ event.customerName }}</span>
              <span class="event-service">{{ event.serviceName }}</span>
              <span v-if="event.stylistName" class="event-stylist">{{ event.stylistName }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * AppCalendar - 通用日曆元件
 * 支援月/週/日三種視圖，仿 Google Calendar 設計
 */
import { ref, computed, watch } from 'vue'
import type { Booking, BookingStatus } from '~/composables/useAdminMockData'

// 型別定義
type CalendarView = 'month' | 'week' | 'day'

interface CalendarEvent extends Booking {}

interface Props {
  /** 初始視圖模式 */
  initialView?: CalendarView
  /** 預約事件資料 */
  events?: CalendarEvent[]
  /** 初始日期 */
  initialDate?: Date
}

// 定義 Props
const props = withDefaults(defineProps<Props>(), {
  initialView: 'month',
  events: () => [],
  initialDate: () => new Date()
})

// 定義事件
const emit = defineEmits<{
  'event-click': [event: CalendarEvent]
  'date-click': [date: string]
  'view-change': [view: CalendarView]
  'date-change': [date: Date]
}>()

// 狀態
const view = ref<CalendarView>(props.initialView)
const currentDate = ref(new Date(props.initialDate))
const selectedDate = ref<string | null>(null)

// 常數
const weekDays = ['週日', '週一', '週二', '週三', '週四', '週五', '週六']
const viewOptions: { value: CalendarView; label: string }[] = [
  { value: 'month', label: '月' },
  { value: 'week', label: '週' },
  { value: 'day', label: '日' }
]
const hours = Array.from({ length: 14 }, (_, i) => i + 8) // 8:00 - 21:00

// 工具函式
const formatDate = (date: Date): string => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const parseDate = (dateStr: string): Date => {
  const [year, month, day] = dateStr.split('-').map(Number)
  return new Date(year, month - 1, day)
}

const isSameDay = (date1: Date, date2: Date): boolean => {
  return date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate()
}

const formatHour = (hour: number): string => {
  return `${String(hour).padStart(2, '0')}:00`
}

// 計算屬性
const currentPeriodTitle = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth() + 1

  if (view.value === 'month') {
    return `${year} 年 ${month} 月`
  } else if (view.value === 'week') {
    const weekStart = getWeekStart(currentDate.value)
    const weekEnd = new Date(weekStart)
    weekEnd.setDate(weekEnd.getDate() + 6)

    if (weekStart.getMonth() === weekEnd.getMonth()) {
      return `${year} 年 ${month} 月 ${weekStart.getDate()} - ${weekEnd.getDate()} 日`
    } else {
      return `${weekStart.getMonth() + 1} 月 ${weekStart.getDate()} 日 - ${weekEnd.getMonth() + 1} 月 ${weekEnd.getDate()} 日`
    }
  } else {
    return `${year} 年 ${month} 月 ${currentDate.value.getDate()} 日`
  }
})

const previousPeriodLabel = computed(() => {
  if (view.value === 'month') return '上個月'
  if (view.value === 'week') return '上週'
  return '前一天'
})

const nextPeriodLabel = computed(() => {
  if (view.value === 'month') return '下個月'
  if (view.value === 'week') return '下週'
  return '後一天'
})

const dayViewTitle = computed(() => {
  const weekDay = weekDays[currentDate.value.getDay()]
  return `${weekDay}`
})

// 月視圖日期
const monthDays = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()

  // 該月第一天
  const firstDay = new Date(year, month, 1)
  // 該月最後一天
  const lastDay = new Date(year, month + 1, 0)

  // 開始日期（上個月的補齊）
  const startDate = new Date(firstDay)
  startDate.setDate(startDate.getDate() - firstDay.getDay())

  // 結束日期（下個月的補齊）
  const endDate = new Date(lastDay)
  const remainingDays = 6 - lastDay.getDay()
  endDate.setDate(endDate.getDate() + remainingDays)

  const days = []
  const current = new Date(startDate)
  const today = new Date()

  while (current <= endDate) {
    days.push({
      date: formatDate(current),
      dayNumber: current.getDate(),
      isCurrentMonth: current.getMonth() === month,
      isToday: isSameDay(current, today)
    })
    current.setDate(current.getDate() + 1)
  }

  return days
})

// 週視圖日期
const weekViewDays = computed(() => {
  const weekStart = getWeekStart(currentDate.value)
  const days = []
  const today = new Date()

  for (let i = 0; i < 7; i++) {
    const date = new Date(weekStart)
    date.setDate(date.getDate() + i)
    days.push({
      date: formatDate(date),
      dayName: weekDays[date.getDay()],
      dayNumber: date.getDate(),
      isToday: isSameDay(date, today)
    })
  }

  return days
})

// 當日事件
const currentDayEvents = computed(() => {
  const dateStr = formatDate(currentDate.value)
  return getEventsForDate(dateStr)
})

// 方法
const getWeekStart = (date: Date): Date => {
  const d = new Date(date)
  const day = d.getDay()
  d.setDate(d.getDate() - day)
  return d
}

const getEventsForDate = (dateStr: string): CalendarEvent[] => {
  return props.events.filter(event => event.date === dateStr)
    .sort((a, b) => a.startTime.localeCompare(b.startTime))
}

const getEventStyle = (event: CalendarEvent) => {
  const [startHour, startMinute] = event.startTime.split(':').map(Number)
  const [endHour, endMinute] = event.endTime.split(':').map(Number)

  const startOffset = (startHour - 8) * 60 + startMinute
  const duration = (endHour * 60 + endMinute) - (startHour * 60 + startMinute)

  const hourHeight = 60 // 每小時 60px
  const top = (startOffset / 60) * hourHeight
  const height = (duration / 60) * hourHeight

  return {
    top: `${top}px`,
    height: `${Math.max(height, 20)}px`
  }
}

const isDateSelected = (dateStr: string): boolean => {
  return selectedDate.value === dateStr
}

// 導航方法
const goToPreviousPeriod = () => {
  const newDate = new Date(currentDate.value)
  if (view.value === 'month') {
    newDate.setMonth(newDate.getMonth() - 1)
  } else if (view.value === 'week') {
    newDate.setDate(newDate.getDate() - 7)
  } else {
    newDate.setDate(newDate.getDate() - 1)
  }
  currentDate.value = newDate
  emit('date-change', newDate)
}

const goToNextPeriod = () => {
  const newDate = new Date(currentDate.value)
  if (view.value === 'month') {
    newDate.setMonth(newDate.getMonth() + 1)
  } else if (view.value === 'week') {
    newDate.setDate(newDate.getDate() + 7)
  } else {
    newDate.setDate(newDate.getDate() + 1)
  }
  currentDate.value = newDate
  emit('date-change', newDate)
}

const goToToday = () => {
  currentDate.value = new Date()
  emit('date-change', currentDate.value)
}

const setView = (newView: CalendarView) => {
  view.value = newView
  emit('view-change', newView)
}

// 事件處理
const handleDateClick = (dateStr: string) => {
  selectedDate.value = dateStr
  emit('date-click', dateStr)
}

const handleEventClick = (event: CalendarEvent) => {
  emit('event-click', event)
}

const handleMoreClick = (dateStr: string) => {
  // 點擊「更多」時切換到日視圖
  currentDate.value = parseDate(dateStr)
  view.value = 'day'
  emit('view-change', 'day')
}

// 監聽外部日期變化
watch(() => props.initialDate, (newDate) => {
  currentDate.value = new Date(newDate)
})
</script>

<style scoped>
.app-calendar {
  background-color: var(--color-bg-card);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

/* ========================================
   日曆頭部
   ======================================== */
.calendar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
}

.calendar-nav {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  padding: 0 var(--spacing-sm);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.nav-btn:hover {
  background-color: var(--color-bg-hover);
  border-color: var(--color-primary);
}

.nav-icon {
  font-size: var(--font-size-lg);
  line-height: 1;
}

.today-btn {
  padding: 0 var(--spacing-md);
}

.calendar-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
}

.calendar-view-switcher {
  display: flex;
  background-color: var(--color-bg);
  border-radius: var(--radius-md);
  padding: 2px;
}

.view-btn {
  padding: var(--spacing-xs) var(--spacing-md);
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.view-btn:hover {
  color: var(--color-text-primary);
}

.view-btn.active {
  background-color: var(--color-bg-card);
  color: var(--color-primary);
  font-weight: 500;
  box-shadow: var(--shadow-sm);
}

/* ========================================
   月視圖
   ======================================== */
.calendar-month {
  padding: var(--spacing-md);
}

.month-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  margin-bottom: var(--spacing-sm);
}

.month-header-cell {
  padding: var(--spacing-sm);
  text-align: center;
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
}

.month-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background-color: var(--color-border-light);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.month-cell {
  min-height: 100px;
  background-color: var(--color-bg-card);
  padding: var(--spacing-xs);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.month-cell:hover {
  background-color: var(--color-bg-hover);
}

.month-cell.other-month {
  background-color: var(--color-bg);
}

.month-cell.other-month .date-number {
  color: var(--color-text-muted);
}

.month-cell.today {
  background-color: var(--color-primary-light);
}

.month-cell.today .date-number {
  color: var(--color-primary);
  font-weight: 600;
}

.month-cell.selected {
  box-shadow: inset 0 0 0 2px var(--color-primary);
}

.cell-header {
  margin-bottom: var(--spacing-xs);
}

.date-number {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.cell-events {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.event-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: 2px var(--spacing-xs);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  cursor: pointer;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.event-time {
  flex-shrink: 0;
  font-weight: 500;
}

.event-title {
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 事件狀態顏色 */
.event-pending {
  background-color: var(--color-warning-light);
  color: #B45309;
}

.event-confirmed {
  background-color: var(--color-success-light);
  color: var(--color-success);
}

.event-completed {
  background-color: var(--color-bg-hover);
  color: var(--color-text-secondary);
}

.event-cancelled_by_customer,
.event-cancelled_by_salon {
  background-color: var(--color-error-light);
  color: var(--color-error);
  text-decoration: line-through;
}

.event-no_show {
  background-color: var(--color-error-light);
  color: var(--color-error);
}

.more-events {
  padding: 2px var(--spacing-xs);
  font-size: var(--font-size-xs);
  color: var(--color-primary);
  cursor: pointer;
}

.more-events:hover {
  text-decoration: underline;
}

/* ========================================
   週視圖
   ======================================== */
.calendar-week {
  display: flex;
  flex-direction: column;
  height: 600px;
}

.week-header {
  display: flex;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.time-gutter {
  width: 60px;
  flex-shrink: 0;
}

.week-header-cell {
  flex: 1;
  padding: var(--spacing-sm);
  text-align: center;
  border-left: 1px solid var(--color-border-light);
}

.week-header-cell.today {
  background-color: var(--color-primary-light);
}

.week-header-cell .day-name {
  display: block;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.week-header-cell .day-number {
  display: block;
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
}

.week-header-cell.today .day-number {
  color: var(--color-primary);
}

.week-body {
  display: flex;
  flex: 1;
  overflow-y: auto;
}

.time-column {
  width: 60px;
  flex-shrink: 0;
}

.time-slot {
  height: 60px;
  padding-right: var(--spacing-sm);
  text-align: right;
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  border-top: 1px solid transparent;
}

.time-slot:first-child {
  margin-top: -8px;
}

.week-grid {
  display: flex;
  flex: 1;
}

.week-column {
  flex: 1;
  position: relative;
  border-left: 1px solid var(--color-border-light);
}

.week-column.today {
  background-color: rgba(63, 124, 106, 0.03);
}

.hour-cell {
  height: 60px;
  border-top: 1px solid var(--color-border-light);
}

.week-event {
  position: absolute;
  left: 2px;
  right: 2px;
  padding: var(--spacing-xs);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  overflow: hidden;
  cursor: pointer;
  z-index: 1;
}

.week-event:hover {
  z-index: 2;
  box-shadow: var(--shadow-md);
}

.week-event .event-content {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.week-event .event-time {
  font-weight: 500;
}

.week-event .event-service {
  color: inherit;
  opacity: 0.8;
}

/* ========================================
   日視圖
   ======================================== */
.calendar-day {
  display: flex;
  flex-direction: column;
  height: 600px;
}

.day-header {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
  text-align: center;
}

.day-title {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
}

.day-body {
  display: flex;
  flex: 1;
  overflow-y: auto;
}

.day-content {
  flex: 1;
  position: relative;
}

.day-content .hour-cell {
  height: 60px;
  border-top: 1px solid var(--color-border-light);
}

.day-event {
  position: absolute;
  left: var(--spacing-sm);
  right: var(--spacing-sm);
  padding: var(--spacing-sm);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  cursor: pointer;
  z-index: 1;
}

.day-event:hover {
  z-index: 2;
  box-shadow: var(--shadow-md);
}

.day-event .event-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.day-event .event-time {
  font-weight: 600;
}

.day-event .event-title {
  font-weight: 500;
}

.day-event .event-service {
  opacity: 0.9;
}

.day-event .event-stylist {
  font-size: var(--font-size-xs);
  opacity: 0.8;
}

/* ========================================
   響應式調整
   ======================================== */
@media (max-width: 768px) {
  .calendar-header {
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .calendar-nav {
    order: 2;
  }

  .calendar-title {
    order: 1;
  }

  .calendar-view-switcher {
    order: 3;
  }

  .month-cell {
    min-height: 80px;
  }

  .event-item {
    padding: 1px var(--spacing-xs);
  }

  .event-time {
    display: none;
  }

  .calendar-week,
  .calendar-day {
    height: 500px;
  }
}
</style>
