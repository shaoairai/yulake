# 約來客 Yulake - 後端開發檢查清單

> 本文件詳細列出從資料庫設計到前後端串接的完整開發任務清單

---

## 目錄

1. [Phase 1: 資料庫設計](#phase-1-資料庫設計)
2. [Phase 2: 後端專案建置](#phase-2-後端專案建置)
3. [Phase 3: API 開發](#phase-3-api-開發)
4. [Phase 4: 前後端串接](#phase-4-前後端串接)
5. [Phase 5: 測試](#phase-5-測試)

---

## Phase 1: 資料庫設計

### 1.1 選擇資料庫技術
- [ ] 決定使用的資料庫系統（建議：PostgreSQL 或 MySQL）
- [ ] 確認 Docker 化部署方案
- [ ] 建立 docker-compose 資料庫服務設定

### 1.2 設計資料表結構

#### 1.2.1 店家相關表
- [ ] **salons（店家）**
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

- [ ] **salon_owners（店家管理員）**
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

- [ ] **business_hours（營業時間）**
  - `id` - 主鍵 UUID
  - `salon_id` - 外鍵關聯 salons
  - `day_of_week` - 星期幾（0-6，0=週日）
  - `is_open` - 是否營業
  - `open_time` - 開始時間
  - `close_time` - 結束時間
  - `created_at` - 建立時間
  - `updated_at` - 更新時間

- [ ] **booking_rules（預約規則）**
  - `id` - 主鍵 UUID
  - `salon_id` - 外鍵關聯 salons（唯一）
  - `slot_interval` - 預約時段間隔（分鐘）
  - `min_advance_hours` - 最少提前預約小時數
  - `max_advance_days` - 最多可預約天數
  - `require_confirmation` - 是否需要店家確認
  - `created_at` - 建立時間
  - `updated_at` - 更新時間

#### 1.2.2 設計師相關表
- [ ] **stylists（設計師）**
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

- [ ] **stylist_schedules（設計師排班）**
  - `id` - 主鍵 UUID
  - `stylist_id` - 外鍵關聯 stylists
  - `day_of_week` - 星期幾（0-6）
  - `is_working` - 是否出勤
  - `start_time` - 開始時間
  - `end_time` - 結束時間
  - `created_at` - 建立時間
  - `updated_at` - 更新時間

- [ ] **stylist_breaks（設計師休息時間/特殊休假）**
  - `id` - 主鍵 UUID
  - `stylist_id` - 外鍵關聯 stylists
  - `date` - 日期（特定日期休假用）
  - `start_time` - 開始時間
  - `end_time` - 結束時間
  - `reason` - 原因
  - `created_at` - 建立時間

#### 1.2.3 服務相關表
- [ ] **services（服務項目）**
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

- [ ] **service_stylists（服務-設計師關聯）**
  - `id` - 主鍵 UUID
  - `service_id` - 外鍵關聯 services
  - `stylist_id` - 外鍵關聯 stylists
  - `created_at` - 建立時間
  - 唯一約束：(service_id, stylist_id)

#### 1.2.4 顧客相關表
- [ ] **customers（顧客）**
  - `id` - 主鍵 UUID
  - `name` - 姓名
  - `email` - Email（唯一，登入用）
  - `password_hash` - 密碼雜湊
  - `phone` - 手機（選填，聯絡用）
  - `birthday` - 生日（選填）
  - `is_active` - 是否啟用
  - `created_at` - 建立時間
  - `updated_at` - 更新時間

- [ ] **salon_customers（店家-顧客關聯與備註）**
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
- [ ] **bookings（預約）**
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
- [ ] **customer_stats（顧客統計快取）**
  - `id` - 主鍵 UUID
  - `salon_id` - 外鍵關聯 salons
  - `customer_id` - 外鍵關聯 customers
  - `total_bookings` - 總預約次數
  - `completed_bookings` - 已完成次數
  - `no_show_count` - 爽約次數
  - `updated_at` - 更新時間
  - 唯一約束：(salon_id, customer_id)

### 1.3 建立資料庫
- [ ] 撰寫 SQL 建表腳本（或使用 ORM migration）
- [ ] 建立索引以優化查詢效能
- [ ] 建立外鍵約束確保資料完整性
- [ ] 撰寫種子資料（Seed Data）腳本
- [ ] 建立測試用假資料

### 1.4 資料庫文件
- [ ] 繪製 ER Diagram（實體關係圖）
- [ ] 撰寫資料字典文件

---

## Phase 2: 後端專案建置

### 2.1 技術選型
- [ ] 決定後端框架（建議：Node.js + Express/Fastify 或 Python + FastAPI）
- [ ] 決定 ORM 工具（建議：Prisma、TypeORM 或 SQLAlchemy）
- [ ] 決定認證方案（JWT Token）
- [ ] 決定 API 文件工具（Swagger/OpenAPI）

### 2.2 專案初始化
- [ ] 建立後端專案目錄結構
- [ ] 初始化專案（package.json 或 pyproject.toml）
- [ ] 安裝必要依賴套件
- [ ] 設定 TypeScript（如使用 Node.js）
- [ ] 設定 ESLint/Prettier 程式碼規範
- [ ] 建立環境變數設定檔（.env.example）

### 2.3 專案架構設計
- [ ] 設計目錄結構：
  ```
  yulakeback/
  ├── src/
  │   ├── config/          # 設定檔
  │   ├── controllers/     # 控制器
  │   ├── middlewares/     # 中介層
  │   ├── models/          # 資料模型
  │   ├── routes/          # 路由定義
  │   ├── services/        # 業務邏輯
  │   ├── utils/           # 工具函式
  │   ├── validators/      # 驗證器
  │   └── app.ts           # 應用程式入口
  ├── prisma/              # Prisma schema & migrations
  ├── tests/               # 測試檔案
  └── docker-compose.yml   # Docker 設定
  ```

### 2.4 基礎設施建置
- [ ] 設定資料庫連線
- [ ] 設定 CORS 跨域
- [ ] 設定錯誤處理中介層
- [ ] 設定請求日誌記錄
- [ ] 設定 API 回應格式標準化
- [ ] 設定 JWT 認證中介層
- [ ] 建立 Docker 開發環境

### 2.5 共用模組開發
- [ ] 建立統一回應格式工具（ApiResponse）
- [ ] 建立錯誤碼定義與錯誤處理
- [ ] 建立分頁查詢工具
- [ ] 建立日期時間處理工具
- [ ] 建立密碼加密/驗證工具

---

## Phase 3: API 開發

### 3.1 認證相關 API

#### 3.1.1 顧客認證
- [ ] `POST /api/auth/customer/register` - 顧客註冊
  - 請求：name, email, password, phone（選填）
  - 驗證：Email 格式、Email 不可重複、密碼強度
  - 回應：token, user 資訊
- [ ] `POST /api/auth/customer/login` - 顧客登入
  - 請求：email, password
  - 驗證：帳號密碼正確性
  - 回應：token, user 資訊
- [ ] `GET /api/auth/customer/me` - 取得當前顧客資訊
  - 需要：Bearer Token
  - 回應：顧客資訊

#### 3.1.2 店家認證
- [ ] `POST /api/auth/salon/login` - 店家登入
  - 請求：email, password
  - 驗證：帳號密碼正確性
  - 回應：token, owner 資訊, salon 資訊
- [ ] `GET /api/auth/salon/me` - 取得當前店家資訊
  - 需要：Bearer Token
  - 回應：owner 資訊, salon 資訊

### 3.2 公開 API（顧客預約前台）

#### 3.2.1 店家資訊
- [ ] `GET /api/salons/:code` - 根據 code 取得店家資訊
  - 回應：店家名稱、Logo、主題色、營業時間等
  - 注意：過濾掉敏感資訊

#### 3.2.2 服務列表
- [ ] `GET /api/salons/:code/services` - 取得店家服務列表
  - 回應：已啟用的服務列表（名稱、說明、時長、價格）
  - 排序：依 sort_order

#### 3.2.3 設計師列表
- [ ] `GET /api/salons/:code/stylists` - 取得店家設計師列表
  - 可選參數：service_id（篩選可服務該項目的設計師）
  - 回應：已啟用的設計師列表（姓名、風格、簡介）
  - 排序：依 sort_order

#### 3.2.4 可用時段
- [ ] `GET /api/salons/:code/available-slots` - 取得可預約時段
  - 必要參數：stylist_id, date, service_id
  - 邏輯：
    1. 取得該日設計師排班
    2. 取得該日既有預約
    3. 計算服務所需時間
    4. 套用預約規則（最晚預約時間）
    5. 產生可用時段列表
  - 回應：可用時段陣列（start_time, end_time）

#### 3.2.5 建立預約
- [ ] `POST /api/bookings` - 建立預約
  - 需要：Bearer Token（顧客）
  - 請求：salon_code, service_id, stylist_id, booking_date, start_time, customer_note
  - 驗證：
    1. 時段是否仍可用（防止併發衝突）
    2. 顧客是否在該店黑名單
    3. 是否符合預約規則
  - 邏輯：
    1. 計算 end_time
    2. 建立預約記錄
    3. 更新顧客統計
    4. 更新 salon_customers（如首次預約）
  - 回應：預約詳情

### 3.3 顧客 API

#### 3.3.1 我的預約
- [ ] `GET /api/me/bookings` - 取得我的預約列表
  - 需要：Bearer Token（顧客）
  - 可選參數：status, page, limit
  - 回應：預約列表（含店家、服務、設計師資訊）

- [ ] `GET /api/me/bookings/:id` - 取得預約詳情
  - 需要：Bearer Token（顧客）
  - 驗證：預約屬於該顧客
  - 回應：預約詳情

- [ ] `PUT /api/me/bookings/:id/cancel` - 取消預約
  - 需要：Bearer Token（顧客）
  - 驗證：預約屬於該顧客、狀態可取消
  - 回應：更新後的預約

### 3.4 店家後台 API

#### 3.4.1 總覽/統計
- [ ] `GET /api/salon/dashboard` - 取得總覽數據
  - 需要：Bearer Token（店家）
  - 回應：
    - 本週預約總數與變化百分比
    - 爽約次數與變化百分比
    - 新顧客數與變化百分比
    - 今日預約列表
    - 回訪/生日提醒列表

#### 3.4.2 預約管理
- [ ] `GET /api/salon/bookings` - 取得預約列表
  - 需要：Bearer Token（店家）
  - 可選參數：date_from, date_to, stylist_id, status, page, limit
  - 回應：預約列表（含顧客、服務、設計師資訊）

- [ ] `GET /api/salon/bookings/:id` - 取得預約詳情
  - 需要：Bearer Token（店家）
  - 回應：完整預約詳情

- [ ] `PUT /api/salon/bookings/:id/status` - 更新預約狀態
  - 需要：Bearer Token（店家）
  - 請求：status, note（選填）
  - 驗證：狀態轉換合法性
  - 邏輯：
    - 若標記 no_show，更新顧客爽約統計
    - 若標記 completed，更新顧客完成統計
  - 回應：更新後的預約

#### 3.4.3 顧客管理
- [ ] `GET /api/salon/customers` - 取得顧客列表
  - 需要：Bearer Token（店家）
  - 可選參數：search, is_blacklisted, page, limit
  - 回應：顧客列表（含統計數據）

- [ ] `GET /api/salon/customers/:id` - 取得顧客詳情
  - 需要：Bearer Token（店家）
  - 回應：顧客資訊、統計、預約歷史、備註

- [ ] `PUT /api/salon/customers/:id/note` - 更新顧客備註
  - 需要：Bearer Token（店家）
  - 請求：note
  - 回應：更新後的顧客資訊

- [ ] `POST /api/salon/customers/:id/blacklist` - 加入黑名單
  - 需要：Bearer Token（店家）
  - 請求：reason（選填）
  - 回應：更新後的顧客資訊

- [ ] `DELETE /api/salon/customers/:id/blacklist` - 解除黑名單
  - 需要：Bearer Token（店家）
  - 回應：更新後的顧客資訊

#### 3.4.4 服務管理
- [ ] `GET /api/salon/services` - 取得服務列表
  - 需要：Bearer Token（店家）
  - 回應：所有服務列表（含停用）

- [ ] `POST /api/salon/services` - 新增服務
  - 需要：Bearer Token（店家）
  - 請求：name, description, duration, price, stylist_ids, is_active
  - 驗證：必填欄位、數值合理性
  - 回應：新增的服務

- [ ] `PUT /api/salon/services/:id` - 更新服務
  - 需要：Bearer Token（店家）
  - 請求：name, description, duration, price, stylist_ids, is_active
  - 回應：更新後的服務

- [ ] `DELETE /api/salon/services/:id` - 刪除服務
  - 需要：Bearer Token（店家）
  - 驗證：無進行中的預約使用此服務
  - 回應：成功/失敗

#### 3.4.5 設計師管理
- [ ] `GET /api/salon/stylists` - 取得設計師列表
  - 需要：Bearer Token（店家）
  - 回應：所有設計師列表（含停用）

- [ ] `POST /api/salon/stylists` - 新增設計師
  - 需要：Bearer Token（店家）
  - 請求：name, style, introduction, is_active
  - 回應：新增的設計師

- [ ] `PUT /api/salon/stylists/:id` - 更新設計師
  - 需要：Bearer Token（店家）
  - 請求：name, style, introduction, is_active
  - 回應：更新後的設計師

- [ ] `DELETE /api/salon/stylists/:id` - 刪除設計師
  - 需要：Bearer Token（店家）
  - 驗證：無進行中的預約指派此設計師
  - 回應：成功/失敗

#### 3.4.6 店家設定
- [ ] `GET /api/salon/settings` - 取得店家設定
  - 需要：Bearer Token（店家）
  - 回應：店家資料、營業時間、預約規則

- [ ] `PUT /api/salon/settings` - 更新店家基本資料
  - 需要：Bearer Token（店家）
  - 請求：name, address, phone, line_id, ig_account, website
  - 回應：更新後的店家資料

- [ ] `PUT /api/salon/settings/hours` - 更新營業時間
  - 需要：Bearer Token（店家）
  - 請求：business_hours 陣列
  - 回應：更新後的營業時間

- [ ] `PUT /api/salon/settings/rules` - 更新預約規則
  - 需要：Bearer Token（店家）
  - 請求：slot_interval, min_advance_hours, max_advance_days, require_confirmation
  - 回應：更新後的預約規則

### 3.5 API 文件
- [ ] 設定 Swagger/OpenAPI
- [ ] 為所有 API 撰寫文件
- [ ] 標註請求/回應範例
- [ ] 標註錯誤碼說明

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
