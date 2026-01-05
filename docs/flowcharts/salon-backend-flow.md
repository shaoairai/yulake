# 約來客 Yulake - 店家後台流程圖

> 店家／廠商在 Yulake 後台的操作流程

## 1. 店家 Onboarding 流程圖

```mermaid
flowchart TD
    Start((開始)) --> Register["店家註冊帳號"]

    Register --> InputBasic["輸入基本資料<br/>・店名<br/>・聯絡人姓名<br/>・Email<br/>・手機<br/>・密碼"]

    InputBasic --> CreateAccount["建立店家帳號"]
    CreateAccount --> FirstLogin["首次登入後台"]

    FirstLogin --> Onboarding["進入引導設定流程"]

    subgraph Setup["初始化設定"]
        Onboarding --> SetupShop["1. 店家基本資料"]
        SetupShop --> ShopDetails["・店家名稱<br/>・Logo 上傳<br/>・地址<br/>・電話/LINE/IG<br/>・官網網址"]

        ShopDetails --> SetupHours["2. 營業時間設定"]
        SetupHours --> HoursDetails["・週一～週日營業時段<br/>・預約間隔（30/60分鐘）<br/>・最晚預約時間"]

        HoursDetails --> SetupStylists["3. 設計師設定"]
        SetupStylists --> StylistDetails["・新增設計師<br/>・姓名/介紹<br/>・出勤時間"]

        StylistDetails --> SetupServices["4. 服務項目設定"]
        SetupServices --> ServiceDetails["・服務名稱/說明<br/>・耗時/價格<br/>・關聯設計師"]
    end

    ServiceDetails --> GenerateCode["產生 salon_code"]
    GenerateCode --> GenerateURL["產生預約連結<br/>booking.yulake.com/s/{code}"]
    GenerateURL --> GenerateQR["產生 QR Code"]

    GenerateQR --> Guide["引導放置連結"]
    Guide --> Channels["・WordPress 官網<br/>・IG/FB Bio<br/>・LINE 選單<br/>・Google Maps"]

    Channels --> Complete["設定完成"]
    Complete --> Dashboard["進入後台首頁"]

    style Setup fill:#e3f2fd
```

## 2. 店家日常操作總覽

```mermaid
flowchart TD
    Login((店家登入)) --> Dashboard["後台首頁<br/>今日總覽"]

    Dashboard --> Stats["查看統計數據<br/>・本週預約數<br/>・新顧客數<br/>・爽約次數"]

    Dashboard --> TodayList["今日預約列表"]

    TodayList --> Actions{"日常操作"}

    Actions --> A1["確認預約"]
    Actions --> A2["取消預約"]
    Actions --> A3["標記未出席"]
    Actions --> A4["查看顧客資料"]
    Actions --> A5["管理黑名單"]

    subgraph Navigation["導航選單"]
        Nav1["預約管理"]
        Nav2["顧客管理"]
        Nav3["服務設定"]
        Nav4["設計師設定"]
        Nav5["店家設定"]
    end

    Dashboard --> Navigation

    style Dashboard fill:#c8e6c9
    style Navigation fill:#fff3e0
```

## 3. 預約管理流程圖

```mermaid
flowchart TD
    Start((進入預約管理)) --> FilterPanel["篩選面板"]

    FilterPanel --> Filters["設定篩選條件<br/>・日期範圍<br/>・設計師<br/>・預約狀態"]

    Filters --> LoadList["載入預約列表"]

    LoadList --> BookingList["顯示預約列表"]

    BookingList --> SelectBooking["選擇一筆預約"]

    SelectBooking --> ViewDetail["查看預約詳情"]

    ViewDetail --> DetailInfo["顯示資訊<br/>・顧客姓名/手機<br/>・服務項目<br/>・設計師<br/>・日期時間<br/>・備註<br/>・建立時間"]

    DetailInfo --> StatusActions{"狀態操作"}

    StatusActions --> |"待確認 → 已確認"| Confirm["確認預約"]
    StatusActions --> |"取消預約"| Cancel["取消預約"]
    StatusActions --> |"標記未出席"| NoShow["標記 No-Show"]
    StatusActions --> |"標記完成"| Complete["標記已完成"]
    StatusActions --> |"查看顧客"| GoCustomer["前往顧客頁"]

    Confirm --> UpdateStatus["更新狀態"]
    Cancel --> InputReason["輸入取消原因（選填）"]
    InputReason --> UpdateStatus
    NoShow --> IncrementCount["累加爽約次數"]
    IncrementCount --> UpdateStatus
    Complete --> UpdateStatus

    UpdateStatus --> Refresh["重新載入列表"]
    Refresh --> BookingList

    GoCustomer --> CustomerPage["顧客詳情頁"]

    style FilterPanel fill:#e3f2fd
    style StatusActions fill:#fff3e0
```

## 4. 顧客與黑名單管理流程圖

```mermaid
flowchart TD
    Start((進入顧客管理)) --> CustomerList["顯示顧客列表"]

    CustomerList --> ListInfo["列表資訊<br/>・姓名<br/>・手機<br/>・總預約次數<br/>・爽約次數<br/>・黑名單狀態"]

    ListInfo --> Search["搜尋/篩選顧客"]
    Search --> SelectCustomer["選擇顧客"]

    SelectCustomer --> CustomerDetail["顧客詳情頁"]

    CustomerDetail --> DetailSections["顯示區塊"]

    DetailSections --> BasicInfo["基本資料<br/>・姓名/手機<br/>・註冊時間"]

    DetailSections --> BookingHistory["預約歷史<br/>・所有歷史預約<br/>・每筆狀態"]

    DetailSections --> SalonNote["店家備註<br/>・喜好風格<br/>・注意事項"]

    DetailSections --> BlacklistStatus["黑名單狀態"]

    subgraph BlacklistActions["黑名單操作"]
        BlacklistStatus --> CheckStatus{"目前狀態"}
        CheckStatus --> |"正常"| AddToBlacklist["加入黑名單"]
        CheckStatus --> |"已在黑名單"| RemoveFromBlacklist["解除黑名單"]

        AddToBlacklist --> InputReason["輸入原因（選填）"]
        InputReason --> ConfirmAdd["確認加入"]
        ConfirmAdd --> UpdateBlacklist["更新黑名單"]

        RemoveFromBlacklist --> ConfirmRemove["確認解除"]
        ConfirmRemove --> UpdateBlacklist
    end

    UpdateBlacklist --> RefreshDetail["重新載入詳情"]
    RefreshDetail --> CustomerDetail

    subgraph EditNote["編輯備註"]
        SalonNote --> EditBtn["點擊編輯"]
        EditBtn --> NoteForm["編輯備註表單"]
        NoteForm --> SaveNote["儲存備註"]
        SaveNote --> RefreshDetail
    end

    style BlacklistActions fill:#ffcdd2
    style EditNote fill:#e8f5e9
```

## 5. 服務項目管理流程圖

```mermaid
flowchart TD
    Start((進入服務設定)) --> ServiceList["顯示服務列表"]

    ServiceList --> ListActions{"操作選項"}

    ListActions --> AddNew["新增服務"]
    ListActions --> EditExisting["編輯服務"]
    ListActions --> ToggleStatus["上架/下架"]
    ListActions --> DeleteService["刪除服務"]

    subgraph AddEditFlow["新增/編輯服務"]
        AddNew --> ServiceForm
        EditExisting --> ServiceForm["服務表單"]

        ServiceForm --> InputName["服務名稱"]
        InputName --> InputDesc["服務說明"]
        InputDesc --> InputDuration["所需時間（分鐘）"]
        InputDuration --> InputPrice["價格"]
        InputPrice --> SelectStylists["選擇可服務設計師"]
        SelectStylists --> UploadImage["上傳服務圖片（選填）"]
        UploadImage --> SaveService["儲存服務"]
    end

    SaveService --> Validate{"驗證資料"}
    Validate --> |"通過"| SaveToDB["儲存到資料庫"]
    Validate --> |"失敗"| ShowError["顯示錯誤"]
    ShowError --> ServiceForm

    SaveToDB --> RefreshList["重新載入列表"]
    RefreshList --> ServiceList

    ToggleStatus --> UpdateStatus["更新上架狀態"]
    UpdateStatus --> RefreshList

    DeleteService --> ConfirmDelete{"確認刪除?"}
    ConfirmDelete --> |"是"| DoDelete["執行刪除"]
    ConfirmDelete --> |"否"| ServiceList
    DoDelete --> RefreshList

    style AddEditFlow fill:#e3f2fd
```

## 6. 設計師管理流程圖

```mermaid
flowchart TD
    Start((進入設計師設定)) --> StylistList["顯示設計師列表"]

    StylistList --> ListActions{"操作選項"}

    ListActions --> AddNew["新增設計師"]
    ListActions --> EditExisting["編輯設計師"]
    ListActions --> ManageSchedule["管理排班"]
    ListActions --> ToggleActive["啟用/停用"]

    subgraph AddEditFlow["新增/編輯設計師"]
        AddNew --> StylistForm
        EditExisting --> StylistForm["設計師表單"]

        StylistForm --> InputName["姓名"]
        InputName --> InputIntro["簡短介紹"]
        InputIntro --> UploadAvatar["上傳頭像"]
        UploadAvatar --> InputTags["擅長風格標籤"]
        InputTags --> SelectServices["可服務項目"]
        SelectServices --> SaveStylist["儲存"]
    end

    SaveStylist --> RefreshList["重新載入列表"]
    RefreshList --> StylistList

    subgraph ScheduleFlow["排班設定"]
        ManageSchedule --> ScheduleForm["排班表單"]
        ScheduleForm --> WeeklySchedule["每週固定班表<br/>週一～週日"]
        WeeklySchedule --> SetHours["設定每日時段<br/>開始～結束"]
        SetHours --> SetBreaks["設定休息時間"]
        SetBreaks --> SpecialDays["特殊日期設定<br/>（請假/加班）"]
        SpecialDays --> SaveSchedule["儲存排班"]
        SaveSchedule --> RefreshList
    end

    ToggleActive --> UpdateActive["更新啟用狀態"]
    UpdateActive --> RefreshList

    style AddEditFlow fill:#fce4ec
    style ScheduleFlow fill:#e8f5e9
```

## 7. 店家設定流程圖

```mermaid
flowchart TD
    Start((進入店家設定)) --> SettingsTabs["設定頁籤"]

    SettingsTabs --> Tab1["基本資料"]
    SettingsTabs --> Tab2["營業時間"]
    SettingsTabs --> Tab3["預約規則"]
    SettingsTabs --> Tab4["外觀設定"]
    SettingsTabs --> Tab5["連結管理"]

    subgraph BasicSettings["基本資料設定"]
        Tab1 --> EditBasic["編輯表單"]
        EditBasic --> BasicFields["・店家名稱<br/>・Logo<br/>・地址<br/>・電話<br/>・LINE/IG<br/>・官網 URL"]
        BasicFields --> SaveBasic["儲存"]
    end

    subgraph HoursSettings["營業時間設定"]
        Tab2 --> EditHours["編輯營業時間"]
        EditHours --> DayHours["週一～週日<br/>各日營業時段"]
        DayHours --> Holidays["休假日設定"]
        Holidays --> SaveHours["儲存"]
    end

    subgraph RulesSettings["預約規則設定"]
        Tab3 --> EditRules["編輯規則"]
        EditRules --> RuleFields["・預約間隔（分鐘）<br/>・最晚預約時間<br/>・可預約天數範圍<br/>・是否需要店家確認"]
        RuleFields --> SaveRules["儲存"]
    end

    subgraph ThemeSettings["外觀設定"]
        Tab4 --> EditTheme["編輯外觀"]
        EditTheme --> ThemeFields["・主題顏色<br/>・Banner 圖片<br/>・歡迎訊息"]
        ThemeFields --> PreviewTheme["預覽效果"]
        PreviewTheme --> SaveTheme["儲存"]
    end

    subgraph LinkSettings["連結管理"]
        Tab5 --> ViewLinks["查看連結"]
        ViewLinks --> BookingURL["預約網址<br/>booking.yulake.com/s/{code}"]
        BookingURL --> CopyURL["複製連結"]
        ViewLinks --> QRCode["QR Code"]
        QRCode --> DownloadQR["下載 QR Code"]
    end

    style BasicSettings fill:#e3f2fd
    style HoursSettings fill:#fff3e0
    style RulesSettings fill:#fce4ec
    style ThemeSettings fill:#e8f5e9
    style LinkSettings fill:#f3e5f5
```

## 8. 預約通知流程圖（未來擴充）

```mermaid
flowchart TD
    subgraph Triggers["觸發事件"]
        T1["新預約建立"]
        T2["預約被取消"]
        T3["預約提醒<br/>（預約前 N 小時）"]
        T4["顧客未出席"]
    end

    Triggers --> NotifyEngine["通知引擎"]

    NotifyEngine --> CheckSettings["檢查通知設定"]

    CheckSettings --> Channels{"啟用的通知管道"}

    Channels --> |"Email"| SendEmail["發送 Email"]
    Channels --> |"LINE Notify"| SendLINE["發送 LINE 通知"]
    Channels --> |"SMS"| SendSMS["發送簡訊"]

    SendEmail --> LogNotify["記錄通知日誌"]
    SendLINE --> LogNotify
    SendSMS --> LogNotify

    subgraph Recipients["通知對象"]
        R1["店家"]
        R2["顧客"]
    end

    LogNotify --> Recipients

    style Triggers fill:#fff3e0
    style Recipients fill:#e8f5e9
```

---

## 流程圖渲染說明

請參考 [booking-flow.md](./booking-flow.md) 中的「如何檢視流程圖」章節。
