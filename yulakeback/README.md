# Yulake 預約系統 - 後端

基於 **Flask + Gunicorn + PostgreSQL** 建置的預約系統後端 API。

## 技術棧

- Python 3.12
- Flask 3.1.0
- Flask-SQLAlchemy（ORM）
- PostgreSQL 17
- Gunicorn（生產環境伺服器）

## 快速開始

### Docker 開發環境（推薦）

在專案根目錄（`yulake/`）執行：

```bash
docker-compose -f docker-compose.back.dev.yml up
```

- API：http://localhost:5000
- 資料庫：localhost:5432

### 本機開發

```bash
# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
cp .env.example .env

# 啟動開發伺服器
python app.py
```

## 專案結構

```
yulakeback/
├── app/
│   ├── __init__.py      # Flask 應用程式工廠
│   ├── routes/          # API 路由
│   │   └── main.py
│   ├── models/          # 資料庫模型
│   └── services/        # 業務邏輯
├── app.py               # 應用程式入口
├── gunicorn.conf.py     # Gunicorn 設定
├── requirements.txt     # Python 依賴
└── .env.example         # 環境變數範例
```

## API 端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/` | API 狀態 |
| GET | `/health` | 健康檢查 |

## 部署

在專案根目錄執行部署腳本：

```bash
bash deploy-back.sh
```

### 容器端口

| 服務 | 開發（dev） | 正式（prod） |
|------|------------|-------------|
| 後端 API | 5000 | 5001 |
| PostgreSQL | 5432 | 5433 |

## 資料庫

- 使用者：`yulake`
- 密碼：`yulake`
- 資料庫名稱：`yulake`

連線字串：
```
postgresql://yulake:yulake@localhost:5432/yulake
```
