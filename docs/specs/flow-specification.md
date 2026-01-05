# 約來客 Yulake - 流程規範文件 v1.0

> 本文件定義系統各流程的標準規範，供前後端開發時遵循

---

## 目錄

1. [顧客預約流程規範](#1-顧客預約流程規範)
2. [身份驗證流程規範](#2-身份驗證流程規範)
3. [預約狀態機規範](#3-預約狀態機規範)
4. [店家後台流程規範](#4-店家後台流程規範)
5. [黑名單機制規範](#5-黑名單機制規範)
6. [時段計算規範](#6-時段計算規範)
7. [錯誤處理規範](#7-錯誤處理規範)

---

## 1. 顧客預約流程規範

### 1.1 流程概述

| 步驟 | 名稱 | 必要性 | 說明 |
|------|------|--------|------|
| Step 1 | 選擇服務 | 必要 | 從店家服務清單中選擇一項服務 |
| Step 2 | 選擇設計師 | 必要 | 選擇可提供該服務的設計師 |
| Step 3 | 選擇日期時間 | 必要 | 選擇預約日期與可用時段 |
| Step 4 | 身份確認 | 條件必要 | 未登入時需登入或註冊 |
| Step 5 | 最終確認 | 必要 | 確認預約摘要並送出 |
| Step 6 | 預約完成 | 結果頁 | 顯示預約成功資訊 |

### 1.2 入口規範

**URL 格式**
```
https://booking.yulake.com/s/{salon_code}
```

**必要參數**
| 參數 | 類型 | 說明 |
|------|------|------|
| salon_code | string | 店家唯一識別碼，用於載入店家資料 |

**可選參數（未來擴充）**
| 參數 | 類型 | 說明 |
|------|------|------|
| service | string | 預選服務 ID，自動跳至 Step 2 |
| stylist | string | 預選設計師 ID |
| ref | string | 來源追蹤碼 |

### 1.3 Step 1: 選擇服務

**前置條件**
- salon_code 有效
- 店家資料已載入

**使用者操作**
1. 瀏覽服務卡片列表
2. 點選一個服務卡片
3. 點擊「下一步」

**前端狀態**
```typescript
interface BookingState {
  selectedService: {
    id: string
    name: string
    description: string
    duration: number  // 分鐘
    price: number
  } | null
}
```

**驗證規則**
- 必須選擇一個服務才能進入下一步

**API 呼叫**
- `GET /api/salons/{salon_code}/services` - 取得服務清單

### 1.4 Step 2: 選擇設計師

**前置條件**
- 已選擇服務

**使用者操作**
1. 瀏覽可服務該項目的設計師列表
2. 點選一位設計師
3. 點擊「下一步」

**前端狀態**
```typescript
interface BookingState {
  selectedStylist: {
    id: string
    name: string
    introduction: string
    avatarUrl: string | null
  } | null
}
```

**驗證規則**
- 必須選擇一位設計師才能進入下一步
- 設計師必須能提供已選擇的服務

**API 呼叫**
- `GET /api/salons/{salon_code}/stylists?service_id={id}` - 取得可服務設計師清單

### 1.5 Step 3: 選擇日期時間

**前置條件**
- 已選擇服務
- 已選擇設計師

**使用者操作**
1. 選擇日期（從可選日期範圍中）
2. 系統載入該日可用時段
3. 選擇一個時段
4. 點擊「下一步」

**前端狀態**
```typescript
interface BookingState {
  selectedDate: string      // YYYY-MM-DD
  selectedTime: string      // HH:mm
  selectedEndTime: string   // HH:mm（自動計算）
}
```

**驗證規則**
- 日期必須在可預約範圍內
- 時段必須符合最晚預約時間規則
- 時段不能與既有預約衝突

**API 呼叫**
- `GET /api/salons/{salon_code}/available-slots?stylist_id={id}&date={date}&service_id={id}`

### 1.6 Step 4: 身份確認

**前置條件**
- 已完成 Step 1-3

**邏輯分支**
```
IF localStorage 有有效 token
  AND token 驗證通過
THEN
  跳過此步驟，直接進入 Step 5
ELSE
  顯示登入/註冊選項
```

**登入流程**
| 欄位 | 類型 | 必填 | 驗證 |
|------|------|------|------|
| email | string | Y | 有效 Email 格式 |
| password | string | Y | 最少 6 字元 |

**註冊流程**
| 欄位 | 類型 | 必填 | 驗證 |
|------|------|------|------|
| name | string | Y | 1-50 字元 |
| email | string | Y | 有效 Email 格式，不可重複 |
| password | string | Y | 最少 6 字元 |
| phone | string | N | 台灣手機格式（選填，聯絡用）|

**API 呼叫**
- `POST /api/auth/login` - 登入
- `POST /api/auth/register` - 註冊

### 1.7 Step 5: 最終確認

**前置條件**
- 已完成 Step 1-4
- 使用者已登入

**顯示資訊**
- 店家名稱
- 服務名稱、時長、價格
- 設計師名稱
- 預約日期、時間
- 顧客姓名、手機
- 備註輸入欄位（選填）

**使用者操作**
1. 確認預約資訊
2. 選填備註
3. 點擊「確認送出預約」

**送出資料結構**
```typescript
interface CreateBookingRequest {
  salon_code: string
  service_id: string
  stylist_id: string
  booking_date: string      // YYYY-MM-DD
  start_time: string        // HH:mm
  end_time: string          // HH:mm
  customer_note?: string
}
```

**API 呼叫**
- `POST /api/bookings` - 建立預約

### 1.8 Step 6: 預約完成

**前置條件**
- 預約建立成功

**顯示內容**
- 成功圖示與標題
- 預約摘要資訊
- 操作按鈕：
  - 「查看我的預約」→ `/me/bookings`
  - 「返回店家官網」→ 店家設定的 return URL

---

## 2. 身份驗證流程規範

### 2.1 Token 管理

**儲存位置**
- localStorage: `yulake_access_token`
- localStorage: `yulake_user`（用戶基本資訊快取）

**Token 結構**（建議使用 JWT）
```typescript
interface TokenPayload {
  user_id: string
  email: string
  name: string
  exp: number       // 過期時間
  iat: number       // 簽發時間
}
```

**Token 生命週期**
| 類型 | 有效期 | 用途 |
|------|--------|------|
| Access Token | 7 天 | API 請求驗證 |
| Refresh Token | 30 天 | 換發新 Access Token（未來擴充）|

### 2.2 登入流程規範

**Request**
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "customer@example.com",
  "password": "userpassword"
}
```

**Success Response**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
      "id": "user_123",
      "name": "王小明",
      "email": "customer@example.com"
    }
  }
}
```

**Error Response**
```json
{
  "success": false,
  "error": {
    "code": "AUTH_INVALID_CREDENTIALS",
    "message": "Email 或密碼錯誤"
  }
}
```

### 2.3 註冊流程規範

**Request**
```http
POST /api/auth/register
Content-Type: application/json

{
  "name": "王小明",
  "email": "customer@example.com",
  "password": "userpassword",
  "phone": "0912345678"  // 選填
}
```

**Success Response**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
      "id": "user_123",
      "name": "王小明",
      "email": "customer@example.com"
    }
  }
}
```

**Error Response - Email 已存在**
```json
{
  "success": false,
  "error": {
    "code": "AUTH_EMAIL_EXISTS",
    "message": "此 Email 已註冊"
  }
}
```

---

## 3. 預約狀態機規範

### 3.1 狀態定義

| 狀態碼 | 顯示名稱 | 說明 |
|--------|----------|------|
| `pending` | 待確認 | 預約已建立，等待店家確認 |
| `confirmed` | 已確認 | 店家已確認預約 |
| `cancelled_by_customer` | 顧客取消 | 顧客主動取消 |
| `cancelled_by_salon` | 店家取消 | 店家取消預約 |
| `no_show` | 未出席 | 顧客未依約前往 |
| `completed` | 已完成 | 服務已完成 |

### 3.2 狀態轉換規則

```
┌─────────────────────────────────────────────────────────────┐
│                        狀態轉換矩陣                          │
├──────────┬──────────┬────────────────────┬─────────┬────────┤
│  From    │ To       │ 觸發者             │ 條件     │ 動作   │
├──────────┼──────────┼────────────────────┼─────────┼────────┤
│ pending  │ confirmed│ 店家               │ -       │ -      │
│ pending  │ cancelled_by_customer │ 顧客  │ -       │ -      │
│ pending  │ cancelled_by_salon    │ 店家  │ -       │ -      │
│ confirmed│ completed│ 店家               │ 服務日後│ -      │
│ confirmed│ no_show  │ 店家               │ 服務日後│ +爽約  │
│ confirmed│ cancelled_by_customer │ 顧客  │ 服務前  │ -      │
│ confirmed│ cancelled_by_salon    │ 店家  │ -       │ -      │
└──────────┴──────────┴────────────────────┴─────────┴────────┘
```

### 3.3 No-Show 處理規範

當預約標記為 `no_show` 時：
1. 累加該顧客在該店的爽約次數
2. 記錄爽約時間
3. 店家可依據爽約次數決定是否加入黑名單

---

## 4. 店家後台流程規範

### 4.1 權限控制

| 角色 | 可存取範圍 |
|------|------------|
| 店家管理員 | 僅限自己店家的所有資料 |
| 設計師（未來）| 僅限自己的預約與顧客 |

### 4.2 今日總覽頁規範

**顯示指標**
| 指標 | 計算方式 |
|------|----------|
| 本週預約數 | 當週所有狀態的預約總數 |
| 新顧客數 | 當週首次在本店預約的顧客數 |
| 爽約次數 | 當週 no_show 狀態的預約數 |

**今日預約列表**
- 排序：依預約時間升冪
- 顯示欄位：時間、顧客姓名、服務、設計師、狀態
- 快捷操作：確認、取消、查看詳情

### 4.3 預約管理規範

**篩選條件**
| 欄位 | 類型 | 說明 |
|------|------|------|
| date_from | date | 起始日期 |
| date_to | date | 結束日期 |
| stylist_id | string | 設計師 ID |
| status | string | 預約狀態 |

**API 呼叫**
```http
GET /api/salon/bookings?date_from=2024-01-01&date_to=2024-01-31&status=confirmed
```

### 4.4 顧客管理規範

**顧客列表欄位**
| 欄位 | 說明 |
|------|------|
| name | 顧客姓名 |
| phone | 手機號碼 |
| total_bookings | 總預約次數（該店） |
| no_show_count | 爽約次數（該店） |
| is_blacklisted | 是否在黑名單 |
| last_visit | 最後一次預約日期 |

**顧客詳情頁**
- 基本資料
- 預約歷史列表
- 店家備註（可編輯）
- 黑名單開關

---

## 5. 黑名單機制規範

### 5.1 黑名單資料結構

```typescript
interface Blacklist {
  id: string
  salon_id: string
  user_id: string
  reason?: string
  created_at: datetime
  created_by: string  // 操作人員 ID
}
```

### 5.2 黑名單檢查時機

**檢查點：建立預約 API**

```
1. 收到建立預約請求
2. 提取 user_id 與 salon_id
3. 查詢 blacklist 資料表
4. IF 存在記錄 THEN
     回傳錯誤：BOOKING_USER_BLACKLISTED
   ELSE
     繼續建立預約流程
```

### 5.3 黑名單錯誤回應

```json
{
  "success": false,
  "error": {
    "code": "BOOKING_USER_BLACKLISTED",
    "message": "目前無法使用線上預約，請直接聯繫店家"
  }
}
```

**注意**：錯誤訊息不應明確告知顧客已被加入黑名單

### 5.4 黑名單操作 API

**加入黑名單**
```http
POST /api/salon/blacklist
Content-Type: application/json

{
  "user_id": "user_123",
  "reason": "多次爽約"
}
```

**移除黑名單**
```http
DELETE /api/salon/blacklist/{user_id}
```

---

## 6. 時段計算規範

### 6.1 可預約日期範圍

```
可預約起始日 = 今天 + 最小提前天數（通常為 0 或 1）
可預約結束日 = 今天 + 可預約天數（如 14 或 30 天）
```

### 6.2 可用時段計算邏輯

```
輸入：
  - stylist_id: 設計師 ID
  - date: 日期
  - service_duration: 服務時長（分鐘）
  - slot_interval: 時段間隔（分鐘）

步驟：
1. 取得設計師該日排班時段
2. 取得該日既有預約
3. 取得店家預約規則（最晚預約時間）
4. 產生時段列表：
   FOR 每個時段 IN 排班時段:
     IF 時段 + 服務時長 不超過排班結束時間
        AND 時段不與既有預約衝突
        AND 時段符合最晚預約時間規則
     THEN
       加入可用時段列表
5. 回傳可用時段列表
```

### 6.3 時段衝突判斷

```
預約 A: [start_a, end_a]
預約 B: [start_b, end_b]

衝突條件：NOT (end_a <= start_b OR end_b <= start_a)
即：start_a < end_b AND start_b < end_a
```

### 6.4 最晚預約時間規則

```
若規則為「至少提前 3 小時預約」

current_time = 現在時間
min_booking_time = current_time + 3 小時

可預約時段必須 >= min_booking_time
```

---

## 7. 錯誤處理規範

### 7.1 錯誤碼定義

| 錯誤碼 | HTTP Status | 說明 |
|--------|-------------|------|
| AUTH_INVALID_CREDENTIALS | 401 | 登入失敗：帳號密碼錯誤 |
| AUTH_EMAIL_EXISTS | 400 | 註冊失敗：Email 已存在 |
| AUTH_TOKEN_EXPIRED | 401 | Token 已過期 |
| AUTH_TOKEN_INVALID | 401 | Token 無效 |
| BOOKING_SLOT_UNAVAILABLE | 400 | 時段已被預約 |
| BOOKING_USER_BLACKLISTED | 403 | 使用者在黑名單中 |
| BOOKING_INVALID_TIME | 400 | 預約時間不符合規則 |
| SALON_NOT_FOUND | 404 | 店家不存在 |
| SERVICE_NOT_FOUND | 404 | 服務不存在 |
| STYLIST_NOT_FOUND | 404 | 設計師不存在 |
| VALIDATION_ERROR | 400 | 欄位驗證失敗 |

### 7.2 錯誤回應格式

```typescript
interface ErrorResponse {
  success: false
  error: {
    code: string
    message: string
    details?: Record<string, string[]>  // 欄位驗證錯誤時使用
  }
}
```

### 7.3 前端錯誤處理策略

| 錯誤類型 | 處理方式 |
|----------|----------|
| 401 Unauthorized | 清除 Token，導向登入 |
| 403 Forbidden | 顯示錯誤訊息 |
| 404 Not Found | 顯示「找不到資料」|
| 400 Bad Request | 顯示具體錯誤訊息 |
| 500 Server Error | 顯示「系統錯誤，請稍後再試」|

---

## 附錄 A：API 端點總覽

### 公開 API（無需登入）

| Method | Endpoint | 說明 |
|--------|----------|------|
| GET | /api/salons/{code} | 取得店家資料 |
| GET | /api/salons/{code}/services | 取得服務清單 |
| GET | /api/salons/{code}/stylists | 取得設計師清單 |
| GET | /api/salons/{code}/available-slots | 取得可用時段 |
| POST | /api/auth/login | 登入 |
| POST | /api/auth/register | 註冊 |

### 顧客 API（需登入）

| Method | Endpoint | 說明 |
|--------|----------|------|
| GET | /api/me | 取得當前用戶資料 |
| GET | /api/me/bookings | 取得我的預約列表 |
| POST | /api/bookings | 建立預約 |
| PUT | /api/bookings/{id}/cancel | 取消預約 |

### 店家後台 API（需店家登入）

| Method | Endpoint | 說明 |
|--------|----------|------|
| GET | /api/salon/dashboard | 取得總覽資料 |
| GET | /api/salon/bookings | 取得預約列表 |
| PUT | /api/salon/bookings/{id}/status | 更新預約狀態 |
| GET | /api/salon/customers | 取得顧客列表 |
| GET | /api/salon/customers/{id} | 取得顧客詳情 |
| PUT | /api/salon/customers/{id}/note | 更新顧客備註 |
| POST | /api/salon/blacklist | 加入黑名單 |
| DELETE | /api/salon/blacklist/{user_id} | 移除黑名單 |
| GET | /api/salon/services | 取得服務列表 |
| POST | /api/salon/services | 新增服務 |
| PUT | /api/salon/services/{id} | 更新服務 |
| DELETE | /api/salon/services/{id} | 刪除服務 |
| GET | /api/salon/stylists | 取得設計師列表 |
| POST | /api/salon/stylists | 新增設計師 |
| PUT | /api/salon/stylists/{id} | 更新設計師 |
| GET | /api/salon/settings | 取得店家設定 |
| PUT | /api/salon/settings | 更新店家設定 |

---

## 附錄 B：前端路由規劃

### 顧客前台

| 路由 | 頁面 |
|------|------|
| /s/{salon_code} | 預約入口頁 |
| /s/{salon_code}/booking | 預約流程頁（Wizard）|
| /s/{salon_code}/booking/complete | 預約完成頁 |
| /me/bookings | 我的預約列表 |
| /me/bookings/{id} | 預約詳情 |
| /auth/login | 登入頁（獨立頁面，選用）|
| /auth/register | 註冊頁（獨立頁面，選用）|

### 店家後台

| 路由 | 頁面 |
|------|------|
| /salon/login | 店家登入 |
| /salon/dashboard | 今日總覽 |
| /salon/bookings | 預約管理 |
| /salon/bookings/{id} | 預約詳情 |
| /salon/customers | 顧客管理 |
| /salon/customers/{id} | 顧客詳情 |
| /salon/services | 服務設定 |
| /salon/stylists | 設計師設定 |
| /salon/settings | 店家設定 |

---

## 版本紀錄

| 版本 | 日期 | 變更說明 |
|------|------|----------|
| v1.0 | 2024-01-XX | 初版建立 |
