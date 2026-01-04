# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

這是一個預約系統專案：
- **前端**：Nuxt 4（Vue 3）
- **後端**：Flask + Gunicorn
- **資料庫**：PostgreSQL 17

## 重要規則

### 前端（Nuxt 4）
**所有新建的檔案必須放在 `yulakefront/app/` 資料夾內**：
- 頁面：`app/pages/`
- 元件：`app/components/`
- 佈局：`app/layouts/`
- 中介層：`app/middleware/`
- 插件：`app/plugins/`
- Composables：`app/composables/`
- 工具函式：`app/utils/`

### 後端（Flask）
**所有新建的檔案放在 `yulakeback/app/` 資料夾內**：
- 路由：`app/routes/`
- 模型：`app/models/`
- 服務：`app/services/`

## 專案結構

```
yulake/
├── yulakefront/                    # Nuxt 前端應用
│   ├── app/                        # 【前端主要開發目錄】
│   ├── public/
│   ├── nuxt.config.ts
│   └── package.json
│
├── yulakeback/                     # Flask 後端應用
│   ├── app/                        # 【後端主要開發目錄】
│   │   ├── routes/                 # API 路由
│   │   ├── models/                 # 資料庫模型
│   │   └── services/               # 業務邏輯
│   ├── app.py                      # 應用程式入口
│   ├── gunicorn.conf.py            # Gunicorn 設定
│   └── requirements.txt
│
├── dockerfile/
│   ├── Dockerfile.front.dev
│   ├── Dockerfile.front.prod
│   ├── Dockerfile.back.dev
│   └── Dockerfile.back.prod
│
├── pgdata/                         # PostgreSQL 資料（dev）
├── pgdata-prod/                    # PostgreSQL 資料（prod）
│
├── docker-compose.front.dev.yml
├── docker-compose.front.prod.yml
├── docker-compose.back.dev.yml
├── docker-compose.back.prod.yml
├── deploy-front.sh
└── deploy-back.sh
```

## 技術棧

### 前端
- Nuxt 4.2.2 / Vue 3.5.26
- TypeScript
- ESLint（@nuxt/eslint）
- @nuxt/image

### 後端
- Python 3.12
- Flask 3.1.0
- Flask-SQLAlchemy
- PostgreSQL 17
- Gunicorn

## 常用指令

### 前端（在 `yulakefront/` 目錄下）

```bash
npm run dev          # 開發伺服器
npm run build        # 正式環境建置
npx eslint .         # ESLint 檢查
```

### 後端（在 `yulakeback/` 目錄下）

```bash
python app.py        # 開發伺服器
pip install -r requirements.txt  # 安裝依賴
```

### Docker 開發環境

```bash
# 前端（端口 3500）
docker-compose -f docker-compose.front.dev.yml up

# 後端 + 資料庫（API: 5000, DB: 5432）
docker-compose -f docker-compose.back.dev.yml up
```

### 部署

```bash
bash deploy-front.sh  # 部署前端
bash deploy-back.sh   # 部署後端
```

## 容器配置

| 服務 | Container 名稱 | 開發（dev） | 正式（prod） |
|------|---------------|------------|-------------|
| 前端 | yulakefront-* | 3500 | 3501 |
| 後端 | yulakeback-* | 5000 | 5001 |
| 資料庫 | yulake-db-* | 5432 | 5433 |

## 資料庫連線

```
使用者：yulake
密碼：yulake
資料庫：yulake
連線字串：postgresql://yulake:yulake@db:5432/yulake
```

## Docker 映像檔

- 前端：`shaoairai/yulakefront:latest`
- 後端：`shaoairai/yulakeback:latest`
