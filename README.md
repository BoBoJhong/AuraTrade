# AuraTrade - AI 驅動的智能投資分析系統

> 🚀 **最後更新**: 2026-01-31  
> 📊 **完成度**: 後端 95% | 前端 85% | 整體 90%

## ✨ 核心功能

- ✅ **即時股價追蹤** - 台股/美股即時報價與歷史圖表
- ✅ **AI 智能推薦** - 多維度分析 (技術面 + 基本面 + 新聞情緒)
- ✅ **新聞爬蟲** - Google News RSS + Gemini AI 情緒分析
- ✅ **投資組合** - 持倉管理、交易記錄、損益計算
- ✅ **價格提醒** - 突破/跌破通知 + LINE 推播
- ✅ **自選股管理** - 個人化追蹤清單
- ⚠️ **WebSocket 即時推送** - 後端已完成，前端待整合
- ⚠️ **定時任務** - 新聞爬蟲排程已實作，待啟動

## 🚀 快速開始 (使用 Docker)

### 先決條件

- Docker Desktop 已安裝並運行
- Git

### 啟動專案

```bash
# 1. Clone 專案
git clone <repository-url>
cd AuraTrade

# 2. 複製環境變數範例
cp backend/.env.example backend/.env

# 3. 啟動所有服務
docker-compose up -d

# 4. 查看日誌
docker-compose logs -f

# 5. 停止服務
docker-compose down
```

### 服務端點

- **前端**: <http://localhost:5173>
- **後端 API**: <http://localhost:8000>
- **API 文檔**: <http://localhost:8000/api/docs>
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 📁 專案結構

```
AuraTrade/
├── backend/              # FastAPI 後端
│   ├── apps/
│   │   ├── api/          # API Layer
│   │   ├── services/     # Service Layer
│   │   ├── repositories/ # Repository Layer
│   │   ├── models/       # ORM Models
│   │   └── core/         # Core Configuration
│   ├── tests/            # 測試
│   ├── main.py           # 應用入口
│   └── requirements.txt
│
├── frontend/             # React 前端
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── stores/
│   └── package.json
│
├── docs/                 # 專案文檔
│   ├── PRD.md
│   ├── SRS.md
│   ├── SDD.md
│   └── diagrams/
│
└── docker-compose.yml
```

## 🛠️ 開發指南

### 後端開發

```bash
# 進入後端容器
docker-compose exec backend bash

# 運行測試
pytest

# 查看測試覆蓋率
pytest --cov=apps

# 代碼格式化
black apps/
flake8 apps/
```

### 前端開發

```bash
# 進入前端容器
docker-compose exec frontend sh

# 運行測試
npm test

# 代碼格式化
npm run lint
```

### 資料庫遷移

```bash
# 創建遷移
docker-compose exec backend alembic revision --autogenerate -m "description"

# 執行遷移
docker-compose exec backend alembic upgrade head

# 回滾遷移
docker-compose exec backend alembic downgrade -1
```

## 📚 文檔

- [功能清單 (FEATURES)](./docs/FEATURES.md) - 完整功能列表與實作狀態
- [變更日誌 (CHANGELOG)](./docs/CHANGELOG.md) - 開發進度與版本記錄
- [測試指南 (TESTING_GUIDE)](./TESTING_GUIDE.md) - 功能測試步驟
- [產品需求文檔 (PRD)](./docs/PRD.md)
- [軟體需求規格書 (SRS)](./docs/SRS.md)
- [軟體設計文檔 (SDD)](./docs/SDD.md)
- [架構文檔 (ARCHITECTURE)](./docs/ARCHITECTURE.md)
- [安全規範 (SECURITY)](./docs/SECURITY.md)
- [錯誤處理 (ERROR_HANDLING)](./docs/ERROR_HANDLING.md)
- [環境設置 (ENVIRONMENT_SETUP)](./docs/ENVIRONMENT_SETUP.md)
- [LINE Bot 設置 (LINE_BOT_SETUP)](./docs/LINE_BOT_SETUP.md)

## 📊 API 端點總覽

### 認證
- `POST /api/v1/auth/register` - 用戶註冊
- `POST /api/v1/auth/login` - 用戶登入
- `GET /api/v1/auth/me` - 獲取當前用戶

### 股票查詢
- `GET /api/v1/stocks/search` - 搜尋股票
- `GET /api/v1/stocks/{symbol}` - 即時報價
- `GET /api/v1/stocks/{symbol}/history` - 歷史數據
- `GET /api/v1/stocks/{symbol}/indicators` - 技術指標

### 新聞與AI
- `GET /api/v1/stocks/{symbol}/news` - 查詢新聞
- `POST /api/v1/stocks/{symbol}/news/fetch` - 抓取新聞
- `GET /api/v1/recommendations` - AI 推薦

### 投資組合
- `GET /api/v1/positions` - 持倉列表
- `POST /api/v1/positions` - 新增持倉
- `GET /api/v1/transactions` - 交易記錄

### 自選股與提醒
- `GET /api/v1/watchlist` - 自選股列表
- `POST /api/v1/watchlist` - 新增自選股
- `GET /api/v1/alerts` - 價格提醒

### WebSocket
- `ws://localhost:8000/api/v1/ws/stocks/{symbol}` - 即時價格推送
- `ws://localhost:8000/api/v1/ws/market` - 市場數據推送

完整 API 文檔: http://localhost:8000/api/docs

## 🧪 測試

詳細測試步驟請參考 [測試指南](./TESTING_GUIDE.md)

```bash
# 後端測試
docker-compose exec backend pytest

# 前端測試
docker-compose exec frontend npm test

# 測試特定功能
curl http://localhost:8000/health  # 健康檢查
curl http://localhost:8000/api/v1/stocks/2330.TW  # 台積電股價
```

## 🔧 環境變數設定

複製 `backend/.env.example` 為 `backend/.env` 並設定以下變數：

```env
# 必要 (已提供預設值)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/auratrade
REDIS_URL=redis://redis:6379
SECRET_KEY=your-secret-key-here

# API Keys (選用 - 用於進階功能)
FUGLE_API_KEY=your_fugle_api_key  # 台股即時行情
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key  # 美股數據
GEMINI_API_KEY=your_gemini_api_key  # AI 新聞分析

# LINE Bot (選用 - 用於通知功能)
LINE_NOTIFY_TOKEN=your_line_notify_token
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
```

## 📈 技術棧

**後端**
- FastAPI 0.100+ (異步 Web 框架)
- SQLAlchemy 2.0+ (ORM - 異步模式)
- PostgreSQL 15 (主資料庫)
- Redis 7 (快取層)
- APScheduler (定時任務)
- Google Gemini AI (新聞分析)
- yfinance, feedparser (數據源)
- WebSockets (實時推送)

**前端**
- React 18 + TypeScript
- Vite (構建工具)
- Tailwind CSS (UI 框架)
- Recharts (圖表庫)
- Axios (HTTP 客戶端)
- Zustand (狀態管理)

**DevOps**
- Docker & Docker Compose
- GitHub Actions (CI/CD)
- Alembic (資料庫遷移)

## 🎯 下一步開發計劃

### 優先級 P0 (待整合)
1. **前端整合 WebSocket** - 將 useStockWebSocket 應用到 WatchlistCard
2. **啟動定時任務** - 在 main.py 中啟動 news_scheduler

### 優先級 P1 (優化)
- 推薦結果 Redis 快取
- 五檔報價顯示
- K線圖表組件

### 優先級 P2 (未來)
- 回測系統
- 社群討論
- 手機 App

## 📦 部署

參考 [部署指南](./docs/DEPLOYMENT.md)

## 🤝 貢獻

參考 [貢獻指南](./.github/CONTRIBUTING.md)

## 📄 授權

私有專案 - 保留所有權利

## 👥 團隊

- 開發團隊: AuraTrade Development Team

---

**最後更新**: 2026-01-29  
**版本**: 1.0.0
