# 資料庫安全規範

> **⚠️ 重要：此文件定義資料庫操作的安全規範，所有開發者必須嚴格遵守！**

---

## 核心原則

### 🛡️ 絕對不可刪除客戶資料

無論在任何情況下，都**不可以**因為：
- Docker 容器重啟
- 服務重新部署
- 開發環境更新
- 任何自動化腳本

而導致客戶的業務資料被刪除。

---

## 安全機制

### 1. 自動初始化保護 (`entrypoint.sh`)

後端服務啟動時的檢查流程：

```
啟動服務
    ↓
等待資料庫連線
    ↓
檢查資料表數量 (TABLES_COUNT)
    ↓
檢查是否有業務資料 (HAS_DATA)
    ↓
┌─────────────────────────────────────────────┐
│ 情況 1: TABLES_COUNT = 0                    │
│ → 全新資料庫，執行完整初始化 + 種子資料      │
├─────────────────────────────────────────────┤
│ 情況 2: TABLES_COUNT > 0 且 HAS_DATA = no   │
│ → 有表但無資料，僅執行種子資料              │
├─────────────────────────────────────────────┤
│ 情況 3: TABLES_COUNT > 0 且 HAS_DATA = yes  │
│ → 有資料，完全跳過初始化                    │
│ → 輸出: "Skipping initialization to         │
│         protect existing data"              │
└─────────────────────────────────────────────┘
```

### 2. 種子資料保護 (`seed.py`)

**預設行為**：
- 執行 `python seed.py` 時，會先檢查資料庫是否有資料
- 若已有資料，**立即終止並顯示錯誤**

**強制執行**（危險）：
- 必須使用 `python seed.py --force`
- 會要求輸入 `DELETE ALL DATA` 確認
- 這是唯一能清空資料庫的方式

### 3. 檢查的資料表

系統會檢查以下關鍵表是否有資料：
- `salons` - 店家資料
- `customers` - 顧客資料
- `bookings` - 預約紀錄

只要任一表有資料，就視為「有業務資料」，拒絕重新初始化。

---

## 正確的操作流程

### 全新環境部署

```bash
# 第一次部署，資料庫為空
git clone <repo>
cd yulake
docker-compose -f docker-compose.back.dev.yml up -d

# 系統會自動：
# 1. 建立所有資料表
# 2. 填入種子測試資料
```

### 日常重啟

```bash
# 重啟服務（安全）
docker-compose -f docker-compose.back.dev.yml restart

# 或
docker-compose -f docker-compose.back.dev.yml down
docker-compose -f docker-compose.back.dev.yml up -d

# 系統會：
# 1. 偵測到現有資料
# 2. 跳過所有初始化
# 3. 保留所有資料
```

### 需要重建開發資料庫（危險操作）

```bash
# 進入後端容器
docker exec -it yulakeback-dev bash

# 執行強制重建
python seed.py --force

# 系統會要求輸入確認
# 請輸入 'DELETE ALL DATA' 確認刪除所有資料: DELETE ALL DATA
```

---

## 禁止事項

### ❌ 禁止直接執行的命令

```bash
# 禁止！會刪除所有資料
docker-compose down -v  # -v 會刪除 volume

# 禁止！會刪除資料庫資料夾
rm -rf pgdata/

# 禁止！在容器中直接執行
python -c "from app import db; db.drop_all()"
```

### ❌ 禁止修改的程式碼

不得移除或繞過以下安全檢查：

**seed.py**:
```python
if has_data and not force:
    print("❌ 安全檢查失敗：資料庫已有資料！")
    sys.exit(1)
```

**entrypoint.sh**:
```bash
if [ "$HAS_DATA" = "yes" ]; then
    echo "Skipping initialization to protect existing data."
fi
```

---

## 生產環境注意事項

1. **備份**：生產環境必須設定定期備份
2. **權限**：限制誰能執行 `--force` 操作
3. **日誌**：記錄所有資料庫操作
4. **測試**：在測試環境驗證後才能部署到生產

---

## 問題排解

### Q: 重啟後資料消失了？

檢查：
1. 是否誤用 `docker-compose down -v`
2. 是否刪除了 `pgdata/` 資料夾
3. 檢查 `docker logs yulakeback-dev` 是否有初始化訊息

### Q: 想重建開發資料但被阻擋？

正確做法：
```bash
docker exec -it yulakeback-dev python seed.py --force
```

### Q: 新增欄位後如何更新資料庫？

目前使用 SQLAlchemy 的 `db.create_all()`，它只會建立不存在的表。
對於欄位變更，建議：
1. 開發階段：重建資料庫
2. 生產環境：使用 Flask-Migrate 做資料庫遷移

---

## 版本紀錄

| 版本 | 日期 | 說明 |
|------|------|------|
| v1.0 | 2026-01-06 | 初版建立 |
