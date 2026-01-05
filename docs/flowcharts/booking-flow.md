# 約來客 Yulake - 顧客預約流程圖

> 使用 Mermaid 語法，可在 GitHub、GitLab、Notion、VS Code (Markdown Preview Mermaid Support) 等平台直接渲染

## 1. 總覽流程圖 (High-Level Flow)

```mermaid
flowchart TB
    subgraph Entry["入口來源"]
        WP["WordPress 官網"]
        Social["社群平台<br/>IG/FB/小紅書"]
        LINE["LINE 官方帳號"]
        Google["Google Maps"]
        QR["實體 QR Code"]
        Platform["Yulake 平台入口"]
    end

    subgraph Booking["預約流程"]
        S1["Step 1: 選擇服務"]
        S2["Step 2: 選擇設計師"]
        S3["Step 3: 選擇日期時間"]
        S4["Step 4: 身份確認"]
        S5["Step 5: 最終確認"]
        S6["Step 6: 預約完成"]
    end

    Entry --> |"帶 salon_code"| Load["載入店家資料"]
    Load --> S1
    S1 --> S2
    S2 --> S3
    S3 --> S4
    S4 --> S5
    S5 --> S6

    style Entry fill:#e8f5e9
    style Booking fill:#e3f2fd
```

## 2. 詳細預約流程圖 (Detailed Booking Flow)

```mermaid
flowchart TD
    Start((開始)) --> Entry["使用者點擊預約連結"]
    Entry --> ParseCode["解析 salon_code"]
    ParseCode --> LoadSalon["載入店家資料<br/>・店名、Logo<br/>・主題色<br/>・服務清單<br/>・設計師清單"]

    LoadSalon --> CheckLogin{"檢查登入狀態"}
    CheckLogin --> |"Token 有效"| SetLoggedIn["設定為已登入"]
    CheckLogin --> |"無 Token 或失效"| SetGuest["設定為訪客模式"]

    SetLoggedIn --> Step1
    SetGuest --> Step1

    subgraph Step1Flow["Step 1: 選擇服務"]
        Step1["顯示服務列表"]
        Step1 --> SelectService["使用者選擇服務"]
        SelectService --> SaveService["暫存 selectedService"]
    end

    SaveService --> Step2

    subgraph Step2Flow["Step 2: 選擇設計師"]
        Step2["顯示設計師列表"]
        Step2 --> SelectStylist["使用者選擇設計師"]
        SelectStylist --> SaveStylist["暫存 selectedStylist"]
    end

    SaveStylist --> Step3

    subgraph Step3Flow["Step 3: 選擇日期時間"]
        Step3["顯示可預約日期"]
        Step3 --> SelectDate["使用者選擇日期"]
        SelectDate --> FetchSlots["載入該日可用時段"]
        FetchSlots --> SelectTime["使用者選擇時段"]
        SelectTime --> SaveDateTime["暫存 selectedDate<br/>selectedTime"]
    end

    SaveDateTime --> Step4

    subgraph Step4Flow["Step 4: 身份確認"]
        Step4{"已登入?"}
        Step4 --> |"是"| SkipAuth["跳過驗證"]
        Step4 --> |"否"| ShowAuth["顯示登入/註冊選項"]
        ShowAuth --> AuthChoice{"選擇方式"}
        AuthChoice --> |"已有帳號"| Login["輸入手機+密碼"]
        AuthChoice --> |"新用戶"| Register["輸入姓名+手機+密碼"]
        Login --> CallLogin["呼叫 Login API"]
        Register --> CallRegister["呼叫 Register API"]
        CallLogin --> AuthSuccess["登入成功"]
        CallRegister --> AuthSuccess
    end

    SkipAuth --> Step5
    AuthSuccess --> Step5

    subgraph Step5Flow["Step 5: 最終確認"]
        Step5["顯示預約摘要"]
        Step5 --> InputNote["輸入備註（選填）"]
        InputNote --> ClickSubmit["點擊確認送出"]
        ClickSubmit --> CallAPI["呼叫建立預約 API"]
        CallAPI --> BackendCheck{"後端檢查"}
        BackendCheck --> |"時段衝突"| ErrorSlot["顯示錯誤：時段已被預約"]
        BackendCheck --> |"黑名單"| ErrorBlack["顯示錯誤：無法預約"]
        BackendCheck --> |"通過"| CreateBooking["建立預約記錄"]
        ErrorSlot --> Step3
        ErrorBlack --> EndError((結束))
    end

    CreateBooking --> Step6

    subgraph Step6Flow["Step 6: 預約完成"]
        Step6["顯示成功畫面"]
        Step6 --> ShowSummary["顯示預約摘要"]
        ShowSummary --> Actions["提供操作按鈕"]
        Actions --> ViewBookings["查看我的預約"]
        Actions --> BackToShop["返回店家官網"]
    end

    ViewBookings --> End((結束))
    BackToShop --> End

    style Step1Flow fill:#fff3e0
    style Step2Flow fill:#fce4ec
    style Step3Flow fill:#e8f5e9
    style Step4Flow fill:#e3f2fd
    style Step5Flow fill:#f3e5f5
    style Step6Flow fill:#e0f7fa
```

## 3. 身份驗證流程圖 (Authentication Flow)

```mermaid
flowchart TD
    Start((進入 Step 4)) --> CheckToken{"localStorage<br/>有 Token?"}

    CheckToken --> |"有"| ValidateToken["驗證 Token 有效性"]
    CheckToken --> |"無"| ShowOptions["顯示登入/註冊選項"]

    ValidateToken --> TokenValid{"Token 有效?"}
    TokenValid --> |"是"| LoadUser["載入用戶資料"]
    TokenValid --> |"否"| ClearToken["清除無效 Token"]
    ClearToken --> ShowOptions

    LoadUser --> ToStep5["前往 Step 5"]

    ShowOptions --> UserChoice{"使用者選擇"}

    UserChoice --> |"登入"| LoginForm["登入表單"]
    UserChoice --> |"註冊"| RegisterForm["註冊表單"]

    subgraph LoginProcess["登入流程"]
        LoginForm --> InputLogin["輸入手機 + 密碼"]
        InputLogin --> SubmitLogin["送出登入請求"]
        SubmitLogin --> LoginResult{"登入結果"}
        LoginResult --> |"成功"| SaveToken["儲存 Token"]
        LoginResult --> |"失敗"| LoginError["顯示錯誤訊息"]
        LoginError --> LoginForm
    end

    subgraph RegisterProcess["註冊流程"]
        RegisterForm --> InputRegister["輸入姓名 + 手機 + 密碼"]
        InputRegister --> ValidateInput{"驗證輸入"}
        ValidateInput --> |"格式錯誤"| ShowValidation["顯示驗證錯誤"]
        ShowValidation --> InputRegister
        ValidateInput --> |"通過"| SubmitRegister["送出註冊請求"]
        SubmitRegister --> RegisterResult{"註冊結果"}
        RegisterResult --> |"成功"| AutoLogin["自動登入"]
        RegisterResult --> |"手機已存在"| PhoneExists["顯示：此手機已註冊"]
        PhoneExists --> LoginForm
        AutoLogin --> SaveToken
    end

    SaveToken --> LoadUser

    style LoginProcess fill:#e3f2fd
    style RegisterProcess fill:#e8f5e9
```

## 4. 預約狀態流轉圖 (Booking Status State Machine)

```mermaid
stateDiagram-v2
    [*] --> pending: 顧客送出預約

    pending --> confirmed: 店家確認
    pending --> cancelled_by_customer: 顧客取消
    pending --> cancelled_by_salon: 店家取消

    confirmed --> completed: 服務完成
    confirmed --> no_show: 顧客未出席
    confirmed --> cancelled_by_customer: 顧客取消
    confirmed --> cancelled_by_salon: 店家取消

    completed --> [*]
    no_show --> [*]
    cancelled_by_customer --> [*]
    cancelled_by_salon --> [*]

    note right of pending
        初始狀態
        等待店家確認
    end note

    note right of no_show
        累計爽約次數
        可能觸發黑名單
    end note
```

## 5. 時段選擇邏輯流程圖 (Time Slot Selection Logic)

```mermaid
flowchart TD
    Start((選擇日期)) --> FetchSlots["呼叫 API 取得可用時段"]

    FetchSlots --> ProcessSlots["處理時段資料"]

    ProcessSlots --> CheckRules{"檢查預約規則"}

    CheckRules --> MinAdvance["最晚預約時間檢查<br/>（如：至少提前3小時）"]
    MinAdvance --> FilterPast["過濾已過時段"]
    FilterPast --> CheckConflict["檢查設計師已有預約"]
    CheckConflict --> CheckBreak["檢查休息時間"]
    CheckBreak --> GenerateSlots["產生可選時段列表"]

    GenerateSlots --> DisplaySlots["顯示時段選項"]

    DisplaySlots --> UserSelect["使用者選擇時段"]

    UserSelect --> ValidateSlot{"再次驗證時段"}
    ValidateSlot --> |"已被預約"| ShowError["顯示：時段已被預約"]
    ShowError --> DisplaySlots
    ValidateSlot --> |"可用"| ConfirmSlot["確認選擇"]

    ConfirmSlot --> End((前往 Step 4))

    style CheckRules fill:#fff3e0
```

## 6. 黑名單檢查流程圖 (Blacklist Check Flow)

```mermaid
flowchart TD
    Start((送出預約請求)) --> ExtractData["提取請求資料<br/>user_id, salon_id"]

    ExtractData --> QueryBlacklist["查詢黑名單資料表"]

    QueryBlacklist --> CheckResult{"該用戶在此店<br/>黑名單中?"}

    CheckResult --> |"是"| LogAttempt["記錄嘗試預約"]
    LogAttempt --> ReturnError["回傳錯誤<br/>目前無法使用線上預約<br/>請直接聯繫店家"]
    ReturnError --> End1((結束 - 失敗))

    CheckResult --> |"否"| ContinueBooking["繼續預約流程"]
    ContinueBooking --> CheckSlot{"檢查時段"}
    CheckSlot --> |"衝突"| SlotError["回傳錯誤：時段已被預約"]
    SlotError --> End2((結束 - 失敗))
    CheckSlot --> |"可用"| CreateRecord["建立預約記錄"]
    CreateRecord --> End3((結束 - 成功))

    style CheckResult fill:#ffcdd2
    style CreateRecord fill:#c8e6c9
```

---

## 如何檢視流程圖

### 方法 1: VS Code 擴充套件
安裝 [Markdown Preview Mermaid Support](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid)

### 方法 2: GitHub / GitLab
直接 push 此檔案，平台會自動渲染 Mermaid 圖表

### 方法 3: Mermaid Live Editor
複製 Mermaid 程式碼到 [mermaid.live](https://mermaid.live/) 線上編輯器

### 方法 4: 匯出圖片
使用 [mermaid-cli](https://github.com/mermaid-js/mermaid-cli) 匯出 PNG/SVG：
```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i booking-flow.md -o booking-flow.png
```
