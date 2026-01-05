# Yulake 預約系統 - 前端

基於 **Nuxt 4** 建置的預約系統前端應用。

## 技術棧

- Nuxt 4.2.2
- Vue 3.5.26
- TypeScript
- ESLint（@nuxt/eslint）
- @nuxt/image（圖片最佳化）

## 快速開始

### 本機開發

```bash
# 安裝依賴
npm install

# 啟動開發伺服器（http://localhost:3000）
npm run dev
```

### Docker 開發環境（推薦）

在專案根目錄（`yulake/`）執行：

```bash
docker-compose -f docker-compose.front.dev.yml up
```

開發伺服器：http://localhost:3500

## 專案結構

```
yulakefront/
├── app/                # 主要開發目錄（Nuxt 4 架構）
│   ├── pages/          # 頁面
│   ├── components/     # 元件
│   ├── layouts/        # 佈局
│   ├── composables/    # Composables
│   └── app.vue         # 根元件
├── public/             # 靜態資源
├── nuxt.config.ts      # Nuxt 配置
└── package.json
```

## 指令

| 指令 | 說明 |
|------|------|
| `npm run dev` | 開發伺服器 |
| `npm run build` | 正式環境建置 |
| `npm run preview` | 預覽正式版 |
| `npm run generate` | 靜態網站生成 |
| `npx eslint .` | ESLint 檢查 |

## 部署

在專案根目錄執行部署腳本：

```bash
bash deploy-front.sh
```

腳本會：
1. 建置正式版 Docker 映像檔
2. 推送到 Docker Hub（可選）
3. 啟動正式版容器（可選）

### 容器端口

| 環境 | 端口 |
|------|------|
| 開發（dev） | 3500 |
| 正式（prod） | 3501 |

## 相關文件

- [Nuxt 官方文件](https://nuxt.com/docs/getting-started/introduction)
- [Vue 3 文件](https://vuejs.org/)
