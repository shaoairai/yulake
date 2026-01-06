# 約來客 Yulake - 後端開發檢查清單

> 本文件詳細列出從資料庫設計到前後端串接的完整開發任務清單

---

## 目錄

1. [Phase 0: 前端日曆元件（優先）](#phase-0-前端日曆元件優先)
2. [Phase 1: 資料庫設計](#phase-1-資料庫設計)
3. [Phase 2: 後端專案建置](#phase-2-後端專案建置)
4. [Phase 3: API 開發](#phase-3-api-開發)
5. [Phase 4: 前後端串接](#phase-4-前後端串接)
6. [Phase 5: 測試](#phase-5-測試)

---

## Phase 0: 前端日曆元件（優先）

> 🔥 **優先開發**：日曆視圖是前後台核心功能，需優先製作

### 0.1 日曆元件設計

#### 0.1.1 元件架構
- [x] 建立 `components/ui/AppCalendar.vue` - 通用日曆元件
  - 支援月視圖、週視圖、日視圖切換
  - 仿 Google Calendar 介面設計
  - 支援拖放操作（未來擴充）
  - 響應式設計（桌機/平板/手機）

#### 0.1.2 視圖模式
- [x] **月視圖（Month View）**
  - 顯示整月格子
  - 每格顯示當日預約數量或摘要
  - 點擊日期可展開詳情或切換至日視圖

- [x] **週視圖（Week View）**
  - 橫軸：週一至週日
  - 縱軸：時間軸（依營業時間範圍）
  - 預約區塊顯示於對應時段
  - 顏色區分不同設計師或狀態

- [x] **日視圖（Day View）**
  - 單日時間軸詳細顯示
  - 每位設計師一個欄位（多欄並列）
  - 清楚顯示空檔與已預約時段

#### 0.1.3 日曆元件功能
- [x] 日期導航（上一週/月、下一週/月、返回今天）
- [x] 視圖切換按鈕
- [x] 預約區塊點擊顯示詳情
- [x] 設計師篩選（顯示特定設計師）
- [x] 狀態顏色標示
  - 待確認：黃色
  - 已確認：綠色
  - 已完成：灰色
  - 已取消：紅色刪除線
  - 未出席：紅色

### 0.2 店家後台日曆頁面

- [x] 建立 `pages/admin/calendar.vue` - 店家預約日曆
  - 整合 AppCalendar 元件
  - 預設顯示週視圖
  - 右側或彈窗顯示預約詳情
  - 快速操作：確認、取消、標記完成
  - 設計師篩選下拉選單
  - 新增預約按鈕（點擊空白時段快速建立）

- [x] 更新 `components/admin/AdminSidebar.vue`
  - 新增「預約日曆」導航項目
  - 放置於「預約管理」下方或整合

### 0.3 顧客前台日曆頁面

- [x] 建立 `pages/my/bookings.vue` - 我的預約日曆
  - 顯示該顧客所有預約
  - 預設月視圖
  - 點擊可查看預約詳情
  - 可從此頁面取消預約
  - 支援日曆/列表視圖切換

- [ ] 建立 `pages/s/[code]/booking/calendar.vue` - 預約選擇日曆
  - 選擇日期時顯示月曆
  - 有空檔的日期標示可選
  - 選擇日期後顯示該日可用時段

### 0.4 日曆 API 需求

- [ ] `GET /api/salon/calendar` - 店家日曆資料
  - 參數：start_date, end_date, stylist_id（選填）
  - 回應：指定範圍內所有預約（含顧客、服務資訊）

- [ ] `GET /api/salons/:code/calendar` - 公開日曆資料（顧客端）
  - 參數：start_date, end_date, stylist_id
  - 回應：已預約時段（不含顧客隱私資訊）

---

## Phase 1: 資料庫設計

### 1.1 選擇資料庫技術
- [x] 決定使用的資料庫系統（建議：PostgreSQL 或 MySQL）
- [x] 確認 Docker 化部署方案
- [x] 建立 docker-compose 資料庫服務設定

### 1.2 設計資料表結構

#### 1.2.1 店家相關表
- [x] **salons（店家）**
  - `id` - 主鍵 UUID
  - `code` - 店家代碼（用於 URL，唯一）
  - `name` - 店家名稱
  - `address` - 地址
  - `phone` - 電話
  - `line_id` - LINE 官方帳號
  - `ig_account` - Instagram 帳號
  - `website` - 官方網站
  - `logo_url` - Logo 圖片 URL
  - `theme_color` - 主題色（預設 #3F7C6A）
  - `booking_url` - 預約連結（自動產生）
  - `is_active` - 是否啟用
  - `created_at` - 建立時間
  - `updated_at` - 更新時間

- [x] **salon_owners（店家管理員）**
  - `id` - 主鍵 UUID
  - `salon_id` - 外鍵關聯 salons
  - `name` - 姓名
  - `email` - Email（登入用，唯一）
  - `password_hash` - 密碼雜湊
  - `phone` - 手機
  - `role` - 角色（owner/staff）
  - `is_active` - 是否啟用
  - `created_at` - 建立時間
  - `updated_at` - 更新時間

- [x] **business_hours（營業時間）**
  - `id` - 主鍵 UUID
  - `salon_id` - 外鍵關聯 salons
  - `day_of_week` - 星期幾（0-6，0=週日）
  - `is_open` - 是否營業
  - `open_time` - 開始時間
  - `close_time` - 結束時間
  - `created_at` - 建立時間
  - `updated_at` - 更新時間

- [x] **booking_rules（預約規則）**
  - `id` - 主鍵 UUID
  - `salon_id` - 外鍵關聯 salons（唯一）
  - `slot_interval` - 預約時段間隔（分鐘）
  - `min_advance_hours` - 最少提前預約小時數
  - `max_advance_days` - 最多可預約天數
  - `require_confirmation` - 是否需要店家確認
  - `created_at` - 建立時間
  - `updated_at` - 更新時間

- [x] **special_dates（特殊日期設定）**
  - `id` - 主鍵 UUID
  - `salon_id` - 外鍵關聯 salons
  - `date` - 日期
  - `type` - 類型（closed: 公休 / special_hours: 特殊營業時間）
  - `open_time` - 開始時間（type=special_hours 時使用）
  - `close_time` - 結束時間（type=special_hours 時使用）
  - `reason` - 原因/說明（如：國定假日、店休、特別營業）
  - `created_at` - 建立時間
  - `updated_at` - 更新時間
  - 唯一約束：(salon_id, date)

#### 1.2.2 設計師相關表
- [x] **stylists（設計師）**
  - `id` - 主鍵 UUID
  - `salon_id` - 外鍵關聯 salons
  - `name` - 姓名
  - `style` - 擅長風格
  - `introduction` - 簡介
  - `avatar_url` - 頭像 URL
  - `sort_order` - 排序順序
  - `is_active` - 是否啟用
  - `created_at` - 建立時間
  - `updated_at` - 更新時間

- [x] **stylist_schedules（設計師排班）**
  - `id` - 主鍵 UUID
  - `stylist_id` - 外鍵關聯 stylists
  - `day_of_week` - 星期幾（0-6）
  - `is_working` - 是否出勤
  - `start_time` - 開始時間
  - `end_time` - 結束時間
  - `created_at` - 建立時間
  - `updated_at` - 更新時間

- [x] **stylist_breaks（設計師休息時間/特殊休假）**
  - `id` - 主鍵 UUID
  - `stylist_id` - 外鍵關聯 stylists
  - `date` - 日期（特定日期休假用）
  - `start_time` - 開始時間
  - `end_time` - 結束時間
  - `reason` - 原因
  - `created_at` - 建立時間

#### 1.2.3 服務相關表
- [x] **services（服務項目）**
  - `id` - 主鍵 UUID
  - `salon_id` - 外鍵關聯 salons
  - `name` - 服務名稱
  - `description` - 服務說明
  - `duration` - 所需時間（分鐘）
  - `price` - 價格
  - `image_url` - 服務圖片 URL
  - `sort_order` - 排序順序
  - `is_active` - 是否啟用
  - `created_at` - 建立時間
  - `updated_at` - 更新時間

- [x] **service_stylists（服務-設計師關聯）**
  - `id` - 主鍵 UUID
  - `service_id` - 外鍵關聯 services
  - `stylist_id` - 外鍵關聯 stylists
  - `created_at` - 建立時間
  - 唯一約束：(service_id, stylist_id)

#### 1.2.4 顧客相關表
- [x] **customers（顧客）**
  - `id` - 主鍵 UUID
  - `name` - 姓名
  - `email` - Email（唯一，登入用）
  - `password_hash` - 密碼雜湊
  - `phone` - 手機（選填，聯絡用）
  - `birthday` - 生日（選填）
  - `is_active` - 是否啟用
  - `created_at` - 建立時間
  - `updated_at` - 更新時間

- [x] **salon_customers（店家-顧客關聯與備註）**
  - `id` - 主鍵 UUID
  - `salon_id` - 外鍵關聯 salons
  - `customer_id` - 外鍵關聯 customers
  - `note` - 店家備註
  - `is_blacklisted` - 是否為黑名單
  - `blacklist_reason` - 黑名單原因
  - `blacklisted_at` - 加入黑名單時間
  - `first_visit_at` - 首次預約時間
  - `last_visit_at` - 最後預約時間
  - `created_at` - 建立時間
  - `updated_at` - 更新時間
  - 唯一約束：(salon_id, customer_id)

#### 1.2.5 預約相關表
- [x] **bookings（預約）**
  - `id` - 主鍵 UUID
  - `salon_id` - 外鍵關聯 salons
  - `customer_id` - 外鍵關聯 customers
  - `service_id` - 外鍵關聯 services
  - `stylist_id` - 外鍵關聯 stylists
  - `booking_date` - 預約日期
  - `start_time` - 開始時間
  - `end_time` - 結束時間
  - `status` - 狀態（pending/confirmed/completed/cancelled_by_customer/cancelled_by_salon/no_show）
  - `customer_note` - 顧客備註
  - `salon_note` - 店家備註
  - `cancelled_at` - 取消時間
  - `cancel_reason` - 取消原因
  - `created_at` - 建立時間
  - `updated_at` - 更新時間
  - 索引：(salon_id, booking_date)
  - 索引：(stylist_id, booking_date)
  - 索引：(customer_id)

#### 1.2.6 統計相關表（可選，用於快取統計數據）
- [x] **customer_stats（顧客統計快取）**
  - `id` - 主鍵 UUID
  - `salon_id` - 外鍵關聯 salons
  - `customer_id` - 外鍵關聯 customers
  - `total_bookings` - 總預約次數
  - `completed_bookings` - 已完成次數
  - `no_show_count` - 爽約次數
  - `total_spent` - 累積消費金額
  - `updated_at` - 更新時間
  - 唯一約束：(salon_id, customer_id)

#### 1.2.7 會員等級相關表
- [x] **membership_tiers（會員等級定義）**
  - `id` - 主鍵 UUID
  - `salon_id` - 外鍵關聯 salons
  - `name` - 等級名稱（如：一般會員、銀卡、金卡、VIP）
  - `min_spent` - 最低累積消費金額
  - `min_visits` - 最低來店次數（二擇一或兩者皆需）
  - `discount_percent` - 折扣百分比（如：5 表示 95 折）
  - `benefits` - 等級福利說明（JSON 或文字）
  - `color` - 等級顯示顏色
  - `sort_order` - 排序順序
  - `is_active` - 是否啟用
  - `created_at` - 建立時間
  - `updated_at` - 更新時間

- [x] **customer_memberships（顧客會員等級）**
  - `id` - 主鍵 UUID
  - `salon_id` - 外鍵關聯 salons
  - `customer_id` - 外鍵關聯 customers
  - `tier_id` - 外鍵關聯 membership_tiers
  - `upgraded_at` - 升級時間
  - `expires_at` - 等級到期時間（可選，用於限時等級）
  - `created_at` - 建立時間
  - `updated_at` - 更新時間
  - 唯一約束：(salon_id, customer_id)

#### 1.2.8 行銷推播相關表
- [x] **email_templates（Email 範本）**
  - `id` - 主鍵 UUID
  - `salon_id` - 外鍵關聯 salons（NULL 表示系統範本）
  - `type` - 範本類型（booking_confirm/booking_reminder/birthday/revisit/promotion）
  - `name` - 範本名稱
  - `subject` - 信件主旨
  - `body` - 信件內容（支援變數替換，如 {{customer_name}}）
  - `is_active` - 是否啟用
  - `created_at` - 建立時間
  - `updated_at` - 更新時間

- [x] **email_campaigns（Email 行銷活動）**
  - `id` - 主鍵 UUID
  - `salon_id` - 外鍵關聯 salons
  - `name` - 活動名稱
  - `template_id` - 外鍵關聯 email_templates
  - `target_type` - 目標客群（all/tier/inactive/birthday_month/custom）
  - `target_config` - 目標設定（JSON，如 tier_ids、inactive_days 等）
  - `scheduled_at` - 排程發送時間
  - `sent_at` - 實際發送時間
  - `status` - 狀態（draft/scheduled/sending/sent/cancelled）
  - `total_recipients` - 總收件人數
  - `sent_count` - 已發送數
  - `open_count` - 開啟數
  - `click_count` - 點擊數
  - `created_at` - 建立時間
  - `updated_at` - 更新時間

- [x] **email_logs（Email 發送紀錄）**
  - `id` - 主鍵 UUID
  - `campaign_id` - 外鍵關聯 email_campaigns（可 NULL，用於自動發送）
  - `salon_id` - 外鍵關聯 salons
  - `customer_id` - 外鍵關聯 customers
  - `email` - 收件 Email
  - `type` - 類型（campaign/booking_confirm/booking_reminder/birthday/revisit）
  - `subject` - 實際主旨
  - `status` - 狀態（pending/sent/failed/bounced）
  - `sent_at` - 發送時間
  - `opened_at` - 開啟時間
  - `clicked_at` - 點擊時間
  - `error_message` - 錯誤訊息
  - `created_at` - 建立時間

- [x] **auto_email_rules（自動發信規則）**
  - `id` - 主鍵 UUID
  - `salon_id` - 外鍵關聯 salons
  - `type` - 規則類型
    - `booking_confirm` - 預約確認通知
    - `booking_reminder` - 預約提醒（前 N 小時）
    - `birthday` - 生日祝福（當月/當日）
    - `revisit` - 回訪提醒（超過 N 天未來店）
    - `no_show_warning` - 爽約警告
  - `template_id` - 外鍵關聯 email_templates
  - `config` - 規則設定（JSON）
    - 如 `{"hours_before": 24}` 表示預約前 24 小時發送
    - 如 `{"inactive_days": 60}` 表示 60 天未來店時發送
  - `is_active` - 是否啟用
  - `created_at` - 建立時間
  - `updated_at` - 更新時間

### 1.3 建立資料庫
- [x] 撰寫 SQL 建表腳本（或使用 ORM migration）
- [x] 建立索引以優化查詢效能
- [x] 建立外鍵約束確保資料完整性
- [x] 撰寫種子資料（Seed Data）腳本
- [x] 建立測試用假資料

### 1.4 資料庫文件
- [ ] 繪製 ER Diagram（實體關係圖）
- [ ] 撰寫資料字典文件

---

## Phase 2: 後端專案建置

### 2.1 技術選型
- [x] 決定後端框架（Python + Flask + Gunicorn）
- [x] 決定 ORM 工具（Flask-SQLAlchemy）
- [x] 決定認證方案（JWT Token with PyJWT）
- [x] 決定 API 文件工具（flask-restx / Swagger UI）

### 2.2 專案初始化
- [x] 建立後端專案目錄結構
- [x] 初始化專案（requirements.txt）
- [x] 安裝必要依賴套件
- [x] 設定 Docker 開發環境
- [x] 建立 entrypoint.sh 自動初始化

### 2.3 專案架構設計
- [x] 設計目錄結構：
  ```
  yulakeback/
  ├── app/
  │   ├── __init__.py      # 應用程式入口
  │   ├── models/          # 資料模型
  │   ├── routes/          # API 路由（flask-restx）
  │   ├── services/        # 業務邏輯（預留）
  │   └── utils/           # 工具函式
  ├── app.py               # 啟動檔
  ├── seed.py              # 種子資料
  ├── entrypoint.sh        # Docker entrypoint
  └── requirements.txt     # 依賴套件
  ```

### 2.4 基礎設施建置
- [x] 設定資料庫連線（PostgreSQL）
- [x] 設定 CORS 跨域
- [x] 設定錯誤處理中介層
- [x] 設定 API 回應格式標準化
- [x] 設定 JWT 認證中介層
- [x] 建立 Docker 開發環境
- [x] Swagger UI 文件（/docs）

### 2.5 共用模組開發
- [x] 建立統一回應格式工具（ApiResponse）
- [x] 建立錯誤碼定義與錯誤處理（ErrorCode, ApiError）
- [x] 建立分頁查詢工具（paginate）
- [x] 建立 JWT 認證工具（create_token, verify_token）
- [x] 建立裝飾器（salon_required, customer_required）

---

## Phase 3: API 開發

### 3.1 認證相關 API

#### 3.1.1 顧客認證
- [x] `POST /api/auth/customer/register` - 顧客註冊
- [x] `POST /api/auth/customer/login` - 顧客登入
- [x] `GET /api/auth/customer/me` - 取得當前顧客資訊

#### 3.1.2 店家認證
- [x] `POST /api/auth/salon/login` - 店家登入
- [x] `GET /api/auth/salon/me` - 取得當前店家資訊

### 3.2 公開 API（顧客預約前台）

#### 3.2.1 店家資訊
- [x] `GET /api/salons/:code` - 根據 code 取得店家資訊

#### 3.2.2 服務列表
- [x] `GET /api/salons/:code/services` - 取得店家服務列表

#### 3.2.3 設計師列表
- [x] `GET /api/salons/:code/stylists` - 取得店家設計師列表

#### 3.2.4 可用時段
- [x] `GET /api/salons/:code/available-slots` - 取得可預約時段

#### 3.2.5 建立預約
- [x] `POST /api/bookings` - 建立預約

### 3.3 顧客 API

#### 3.3.1 我的預約
- [x] `GET /api/me/bookings` - 取得我的預約列表
- [x] `GET /api/me/bookings/:id` - 取得預約詳情
- [x] `PUT /api/me/bookings/:id/cancel` - 取消預約
- [x] `GET /api/me/profile` - 取得個人資料
- [x] `PUT /api/me/profile` - 更新個人資料

### 3.4 店家後台 API

#### 3.4.1 總覽/統計
- [x] `GET /api/salon/dashboard` - 取得總覽數據

#### 3.4.2 預約管理
- [x] `GET /api/salon/bookings` - 取得預約列表
- [x] `GET /api/salon/bookings/:id` - 取得預約詳情
- [x] `PUT /api/salon/bookings/:id/status` - 更新預約狀態
- [x] `GET /api/salon/calendar` - 取得日曆資料

#### 3.4.3 顧客管理
- [x] `GET /api/salon/customers` - 取得顧客列表
- [x] `GET /api/salon/customers/:id` - 取得顧客詳情
- [x] `PUT /api/salon/customers/:id/note` - 更新顧客備註
- [x] `POST /api/salon/customers/:id/blacklist` - 加入黑名單
- [x] `DELETE /api/salon/customers/:id/blacklist` - 解除黑名單

#### 3.4.4 服務管理
- [x] `GET /api/salon/services` - 取得服務列表
- [x] `POST /api/salon/services` - 新增服務
- [x] `PUT /api/salon/services/:id` - 更新服務
- [x] `DELETE /api/salon/services/:id` - 刪除服務

#### 3.4.5 設計師管理
- [x] `GET /api/salon/stylists` - 取得設計師列表
- [x] `POST /api/salon/stylists` - 新增設計師
- [x] `PUT /api/salon/stylists/:id` - 更新設計師
- [x] `DELETE /api/salon/stylists/:id` - 刪除設計師

#### 3.4.6 店家設定
- [x] `GET /api/salon/settings` - 取得店家設定
- [x] `PUT /api/salon/settings` - 更新店家基本資料
- [x] `PUT /api/salon/settings/hours` - 更新營業時間
- [x] `PUT /api/salon/settings/rules` - 更新預約規則

#### 3.4.7 特殊日期管理
- [x] `GET /api/salon/special-dates` - 取得特殊日期列表
- [x] `POST /api/salon/special-dates` - 新增特殊日期
- [x] `PUT /api/salon/special-dates/:id` - 更新特殊日期
- [x] `DELETE /api/salon/special-dates/:id` - 刪除特殊日期

#### 3.4.8 會員等級與集點管理
- [x] `GET /api/salon/membership/tiers` - 取得會員等級列表（最多 10 等級）
- [x] `POST /api/salon/membership/tiers` - 新增會員等級
- [x] `GET /api/salon/membership/tiers/:id` - 取得會員等級詳情
- [x] `PUT /api/salon/membership/tiers/:id` - 更新會員等級
- [x] `DELETE /api/salon/membership/tiers/:id` - 刪除會員等級
- [x] `GET /api/salon/membership/customers/:id/tier` - 取得顧客等級
- [x] `PUT /api/salon/membership/customers/:id/tier` - 手動調整顧客等級
- [x] `GET /api/salon/membership/point-rules` - 取得集點規則
- [x] `PUT /api/salon/membership/point-rules` - 更新集點規則
- [x] `GET /api/salon/membership/customers/:id/points` - 取得顧客點數
- [x] `POST /api/salon/membership/customers/:id/points` - 手動調整顧客點數
- [x] `GET /api/salon/membership/customers/:id/points/history` - 取得點數交易紀錄
- [x] `GET /api/salon/membership/stats` - 取得會員等級統計

#### 3.4.9 Email 範本管理
- [x] `GET /api/salon/email/templates` - 取得 Email 範本列表
- [x] `POST /api/salon/email/templates` - 新增 Email 範本
- [x] `GET /api/salon/email/templates/:id` - 取得範本詳情
- [x] `PUT /api/salon/email/templates/:id` - 更新 Email 範本
- [x] `DELETE /api/salon/email/templates/:id` - 刪除 Email 範本
- [x] `POST /api/salon/email/templates/:id/preview` - 預覽 Email 範本

#### 3.4.10 Email 行銷活動
- [x] `GET /api/salon/email/campaigns` - 取得行銷活動列表
- [x] `POST /api/salon/email/campaigns` - 建立行銷活動
- [x] `GET /api/salon/email/campaigns/:id` - 取得活動詳情
- [x] `PUT /api/salon/email/campaigns/:id` - 更新行銷活動
- [x] `DELETE /api/salon/email/campaigns/:id` - 刪除行銷活動
- [x] `POST /api/salon/email/campaigns/:id/send` - 立即發送活動
- [x] `POST /api/salon/email/campaigns/:id/cancel` - 取消排程活動
- [x] `GET /api/salon/email/campaigns/:id/recipients` - 預覽收件人列表

#### 3.4.11 自動發信規則
- [x] `GET /api/salon/email/auto-rules` - 取得自動發信規則
- [x] `GET /api/salon/email/auto-rules/:type` - 取得特定規則
- [x] `PUT /api/salon/email/auto-rules/:type` - 更新自動發信規則

#### 3.4.12 Email 發送紀錄
- [x] `GET /api/salon/email/logs` - 取得發送紀錄（含篩選）

### 3.5 API 文件
- [x] 設定 Swagger/OpenAPI（flask-restx 整合，路徑：/docs）
- [x] 為所有 API 撰寫文件（透過 flask-restx @ns.doc 自動生成）
- [ ] 標註請求/回應範例（進階優化）
- [ ] 標註錯誤碼說明（進階優化）

---

## Phase 4: 前後端串接

### 4.1 前端 API 層建立

#### 4.1.1 HTTP Client 設定
- [ ] 建立 `composables/useApi.ts` - API 呼叫封裝
  - 設定 base URL（從環境變數讀取）
  - 設定請求攔截器（自動帶入 Token）
  - 設定回應攔截器（統一錯誤處理）
  - 處理 401 錯誤（Token 過期）

#### 4.1.2 認證相關
- [ ] 建立 `composables/useAuth.ts` - 認證狀態管理
  - 顧客登入/註冊
  - 店家登入
  - Token 存取（localStorage）
  - 登出清除狀態
  - 自動驗證 Token 有效性

#### 4.1.3 顧客前台 API
- [ ] 建立 `composables/useBookingApi.ts` - 預約相關 API
  - 取得店家資訊
  - 取得服務列表
  - 取得設計師列表
  - 取得可用時段
  - 建立預約
  - 取得我的預約列表
  - 取消預約

#### 4.1.4 店家後台 API
- [ ] 更新 `composables/useAdminMockData.ts` → `composables/useAdminApi.ts`
  - 取得總覽數據
  - 預約管理 CRUD
  - 顧客管理 CRUD
  - 服務管理 CRUD
  - 設計師管理 CRUD
  - 店家設定管理

### 4.2 前端頁面串接

#### 4.2.1 店家後台頁面
- [ ] `pages/admin/index.vue` - 串接 Dashboard API
  - 統計數據
  - 今日預約列表
  - 提醒列表

- [ ] `pages/admin/bookings/index.vue` - 串接預約管理 API
  - 預約列表查詢
  - 篩選功能
  - 狀態變更
  - 預約詳情

- [ ] `pages/admin/customers/index.vue` - 串接顧客管理 API
  - 顧客列表查詢
  - 搜尋與篩選
  - 黑名單切換
  - 備註編輯

- [ ] `pages/admin/services.vue` - 串接服務管理 API
  - 服務列表
  - 新增/編輯服務
  - 啟用/停用服務

- [ ] `pages/admin/stylists.vue` - 串接設計師管理 API
  - 設計師列表
  - 新增/編輯設計師
  - 啟用/停用設計師

- [ ] `pages/admin/settings.vue` - 串接店家設定 API
  - 讀取店家設定
  - 儲存變更
  - 複製預約連結

- [ ] `pages/admin/calendar.vue` - 串接日曆 API
  - 日曆元件整合
  - 預約資料載入
  - 快速操作功能

- [ ] `pages/admin/special-dates.vue` - 串接特殊日期 API（或整合至設定頁）
  - 特殊日期列表
  - 新增/編輯/刪除公休或特殊營業

- [ ] `pages/admin/membership.vue` - 會員等級管理頁面
  - 會員等級列表
  - 新增/編輯等級
  - 設定升級條件與優惠

- [ ] `pages/admin/marketing/index.vue` - Email 行銷總覽
  - 行銷活動列表
  - 發送統計摘要

- [ ] `pages/admin/marketing/campaigns/index.vue` - 行銷活動管理
  - 活動列表
  - 建立新活動
  - 排程/發送/取消

- [ ] `pages/admin/marketing/templates.vue` - Email 範本管理
  - 範本列表
  - 編輯範本內容
  - 預覽功能

- [ ] `pages/admin/marketing/automation.vue` - 自動發信設定
  - 預約確認通知設定
  - 預約提醒設定
  - 生日祝福設定
  - 回訪提醒設定

#### 4.2.2 店家登入頁面
- [ ] 建立 `pages/admin/login.vue` - 店家登入頁
  - Email + 密碼登入表單
  - 登入成功導向 Dashboard
  - 錯誤訊息顯示

#### 4.2.3 顧客前台頁面（如需要）
- [ ] 建立預約流程頁面
- [ ] 建立我的預約頁面
- [ ] 建立登入/註冊頁面

### 4.3 狀態管理優化
- [ ] 建立全域狀態管理（如需要，可用 Pinia）
- [ ] 處理載入狀態顯示
- [ ] 處理錯誤狀態顯示
- [ ] 實作樂觀更新（Optimistic Update）

### 4.4 環境設定
- [ ] 建立 `.env.development` 設定開發環境 API URL
- [ ] 建立 `.env.production` 設定正式環境 API URL
- [ ] 更新 `nuxt.config.ts` 讀取環境變數

---

## Phase 5: 測試

### 5.1 後端單元測試
- [ ] 設定測試框架（Jest/Vitest/Pytest）
- [ ] 建立測試資料庫

#### 5.1.1 工具函式測試
- [ ] 密碼加密/驗證測試
- [ ] JWT Token 產生/驗證測試
- [ ] 日期時間工具測試
- [ ] 時段計算邏輯測試

#### 5.1.2 Service 層測試
- [ ] 認證服務測試
- [ ] 預約服務測試（含時段衝突、黑名單檢查）
- [ ] 顧客服務測試
- [ ] 服務項目服務測試
- [ ] 設計師服務測試

### 5.2 後端 API 測試
- [ ] 設定 API 測試工具（Supertest/Pytest）

#### 5.2.1 認證 API 測試
- [ ] 顧客註冊測試
  - 正常註冊
  - Email 已存在
  - 格式驗證錯誤
- [ ] 顧客登入測試
  - 正常登入
  - 密碼錯誤
  - 帳號不存在
- [ ] 店家登入測試

#### 5.2.2 公開 API 測試
- [ ] 取得店家資訊測試
- [ ] 取得服務列表測試
- [ ] 取得設計師列表測試
- [ ] 取得可用時段測試
  - 正常取得
  - 無可用時段
  - 參數錯誤

#### 5.2.3 預約 API 測試
- [ ] 建立預約測試
  - 正常建立
  - 時段衝突
  - 黑名單顧客
  - 未登入
- [ ] 取消預約測試
- [ ] 狀態變更測試

#### 5.2.4 店家 API 測試
- [ ] 預約管理測試
- [ ] 顧客管理測試
- [ ] 服務管理測試
- [ ] 設計師管理測試

### 5.3 前端測試
- [ ] 設定測試框架（Vitest + Vue Test Utils）

#### 5.3.1 元件測試
- [ ] UI 元件測試（Button, Card, Input, Select, Badge, Modal）
- [ ] Admin 元件測試（Sidebar, Topbar, StatCard, PageHeader）

#### 5.3.2 頁面測試
- [ ] Dashboard 頁面測試
- [ ] 預約管理頁面測試
- [ ] 顧客管理頁面測試

### 5.4 整合測試
- [ ] 完整預約流程測試
  1. 顧客註冊
  2. 選擇服務
  3. 選擇設計師
  4. 選擇時段
  5. 建立預約
  6. 查看我的預約

- [ ] 店家管理流程測試
  1. 店家登入
  2. 查看 Dashboard
  3. 確認預約
  4. 標記完成/未出席
  5. 管理顧客黑名單

### 5.5 效能與安全測試
- [ ] API 回應時間測試
- [ ] 併發預約測試（防止重複預約）
- [ ] SQL Injection 防護測試
- [ ] XSS 防護測試
- [ ] 認證授權測試（越權存取）

### 5.6 手動測試檢查清單

#### 5.6.1 店家後台手動測試
- [ ] 登入功能
  - [ ] 正確帳密可登入
  - [ ] 錯誤帳密顯示錯誤
  - [ ] 登入後導向 Dashboard

- [ ] 今日總覽
  - [ ] 統計數字正確顯示
  - [ ] 今日預約列表正確
  - [ ] 快速操作按鈕可點擊
  - [ ] 提醒列表正確顯示

- [ ] 預約管理
  - [ ] 列表正確載入
  - [ ] 日期篩選功能正常
  - [ ] 設計師篩選功能正常
  - [ ] 狀態篩選功能正常
  - [ ] 可查看預約詳情
  - [ ] 可確認待確認預約
  - [ ] 可標記完成
  - [ ] 可標記未出席（爽約數正確累加）
  - [ ] 可取消預約

- [ ] 顧客管理
  - [ ] 列表正確載入
  - [ ] 搜尋功能正常
  - [ ] 黑名單篩選正常
  - [ ] 可查看顧客詳情
  - [ ] 可編輯備註
  - [ ] 可加入/解除黑名單

- [ ] 服務管理
  - [ ] 列表正確載入
  - [ ] 可新增服務
  - [ ] 可編輯服務
  - [ ] 可啟用/停用服務

- [ ] 設計師管理
  - [ ] 列表正確載入
  - [ ] 可新增設計師
  - [ ] 可編輯設計師
  - [ ] 可啟用/停用設計師

- [ ] 店家設定
  - [ ] 資料正確載入
  - [ ] 可修改基本資料
  - [ ] 可複製預約連結
  - [ ] 儲存後資料正確更新

#### 5.6.2 RWD 測試
- [ ] 桌機版（1920x1080）
- [ ] 平板版（1024x768）
- [ ] 手機版（390x844）

#### 5.6.3 瀏覽器相容性
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge

---

## 附錄 A: 技術建議

### 推薦技術堆疊

**後端**
- Runtime: Node.js 20+
- Framework: Fastify 或 Express
- Language: TypeScript
- ORM: Prisma
- Database: PostgreSQL 16
- Auth: JWT (jsonwebtoken)
- Validation: Zod
- API Docs: Swagger (fastify-swagger)

**開發工具**
- Docker & Docker Compose
- ESLint + Prettier
- Husky (Git hooks)
- Jest/Vitest (Testing)

### 目錄結構建議

```
yulakeback/
├── src/
│   ├── config/
│   │   ├── database.ts
│   │   ├── jwt.ts
│   │   └── env.ts
│   ├── controllers/
│   │   ├── auth.controller.ts
│   │   ├── booking.controller.ts
│   │   ├── customer.controller.ts
│   │   ├── salon.controller.ts
│   │   ├── service.controller.ts
│   │   └── stylist.controller.ts
│   ├── middlewares/
│   │   ├── auth.middleware.ts
│   │   ├── error.middleware.ts
│   │   └── validate.middleware.ts
│   ├── routes/
│   │   ├── auth.routes.ts
│   │   ├── public.routes.ts
│   │   ├── customer.routes.ts
│   │   └── salon.routes.ts
│   ├── services/
│   │   ├── auth.service.ts
│   │   ├── booking.service.ts
│   │   ├── customer.service.ts
│   │   ├── salon.service.ts
│   │   ├── service.service.ts
│   │   └── stylist.service.ts
│   ├── validators/
│   │   ├── auth.validator.ts
│   │   ├── booking.validator.ts
│   │   └── ...
│   ├── utils/
│   │   ├── api-response.ts
│   │   ├── error-codes.ts
│   │   ├── password.ts
│   │   └── time-slots.ts
│   ├── types/
│   │   └── index.ts
│   └── app.ts
├── prisma/
│   ├── schema.prisma
│   ├── migrations/
│   └── seed.ts
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── package.json
└── tsconfig.json
```

---

## 附錄 B: 錯誤碼定義

| 錯誤碼 | HTTP Status | 說明 |
|--------|-------------|------|
| AUTH_INVALID_CREDENTIALS | 401 | 登入失敗：帳號密碼錯誤 |
| AUTH_EMAIL_EXISTS | 400 | 註冊失敗：Email 已存在 |
| AUTH_TOKEN_EXPIRED | 401 | Token 已過期 |
| AUTH_TOKEN_INVALID | 401 | Token 無效 |
| AUTH_UNAUTHORIZED | 403 | 無權限存取 |
| BOOKING_SLOT_UNAVAILABLE | 400 | 時段已被預約 |
| BOOKING_USER_BLACKLISTED | 403 | 使用者在黑名單中 |
| BOOKING_INVALID_TIME | 400 | 預約時間不符合規則 |
| BOOKING_CANNOT_CANCEL | 400 | 此預約無法取消 |
| SALON_NOT_FOUND | 404 | 店家不存在 |
| SERVICE_NOT_FOUND | 404 | 服務不存在 |
| STYLIST_NOT_FOUND | 404 | 設計師不存在 |
| CUSTOMER_NOT_FOUND | 404 | 顧客不存在 |
| VALIDATION_ERROR | 400 | 欄位驗證失敗 |
| INTERNAL_ERROR | 500 | 系統內部錯誤 |

---

## 版本紀錄

| 版本 | 日期 | 變更說明 |
|------|------|----------|
| v1.0 | 2025-01-05 | 初版建立 |
| v1.1 | 2025-01-05 | 顧客登入方式改為 Email |
| v2.0 | 2025-01-05 | 新增功能：日曆元件（Phase 0）、特殊日期設定、會員等級制度、Email 行銷推播 |
