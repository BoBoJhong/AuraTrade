# AuraTrade 功能完整清單

## 📊 **核心功能**

### 1. 用戶認證系統
- ✅ 用戶註冊 (Email + 密碼)
- ✅ 用戶登入 (JWT Token)
- ✅ Token 自動刷新
- ✅ 密碼加密存儲 (bcrypt)
- **API端點**: `/api/v1/auth/register`, `/api/v1/auth/login`

### 2. 股票搜尋與查詢
- ✅ 支援台股 (加 `.TW` 後綴)
- ✅ 支援美股 (直接輸入代號)
- ✅ 即時股價查詢
- ✅ 歷史價格圖表 (5d/1mo/3mo/1y)
- ✅ 自動計算漲跌幅 (當 Yahoo Finance API 返回 null 時)
- **API端點**: `/api/v1/stocks/{symbol}/quote`, `/api/v1/stocks/{symbol}/history`

### 3. 自選股票列表 (Watchlist)
- ✅ 新增/移除自選股
- ✅ 即時價格更新
- ✅ 漲跌幅顯示 (紅漲綠跌)
- ✅ 展開查看歷史圖表
- ✅ 快速跳轉股票詳情頁
- **API端點**: `/api/v1/watchlist`, `/api/v1/watchlist/{symbol}`
- **前端組件**: `WatchlistCard.tsx`

### 4. 價格提醒系統
- ✅ 設定目標價格
- ✅ 突破/跌破提醒
- ✅ 提醒歷史記錄
- ✅ LINE 通知推播 (可選)
- **API端點**: `/api/v1/alerts`, `/api/v1/alerts/check`
- **前端組件**: `AlertModal.tsx`

---

## 📰 **新聞與AI分析** (新功能)

### 5. 智能新聞爬蟲
- ✅ Google News RSS 整合
- ✅ 自動抓取台股/美股新聞
- ✅ 支援多語言 (繁中/英文)
- ✅ 自動清理 HTML 標籤
- ✅ 發布時間智能解析
- **服務**: `GoogleNewsService`
- **API端點**: `/api/v1/stocks/{symbol}/news`

### 6. AI 情緒分析
- ✅ Google Gemini Pro 整合
- ✅ 新聞情緒判斷 (利多/利空/中性)
- ✅ 情緒分數 (-1.0 ~ 1.0)
- ✅ 分析理由說明
- ✅ 投資建議生成
- **服務**: `GeminiService`
- **需要**: `GEMINI_API_KEY` 環境變數

### 7. 定時任務排程
- ✅ APScheduler 背景任務
- ✅ 每小時自動抓取新聞
- ✅ 監控 11 支熱門股票
  - 台股: 2330.TW, 2317.TW, 2454.TW, 2308.TW, 0050.TW, 006208.TW
  - 美股: AAPL, MSFT, GOOGL, TSLA, NVDA
- **服務**: `NewsScheduler`

### 8. 新聞面板組件
- ✅ 時間篩選 (1天/7天/30天)
- ✅ 情緒標籤顯示 (📈📉➡️)
- ✅ 手動更新新聞按鈕
- ✅ 外部連結跳轉
- ✅ 相對時間顯示 (X分鐘前/X小時前)
- **前端組件**: `NewsPanel.tsx`

---

## ⚡ **實時功能** (新功能)

### 9. WebSocket 實時價格更新
- ✅ 雙向 WebSocket 連接
- ✅ 每 5 秒推送價格更新
- ✅ 自動重連機制
- ✅ 連線狀態顯示
- ✅ 支援多股票同時訂閱
- **WebSocket端點**: `/api/v1/ws/stocks/{symbol}`
- **前端Hook**: `useStockWebSocket`

### 10. 市場總覽推播
- ✅ 大盤指數即時更新
- ✅ 加權指數/櫃買指數
- ✅ 每 10 秒更新
- **WebSocket端點**: `/api/v1/ws/market`
- **前端Hook**: `useMarketWebSocket`

---

## 💼 **投資組合管理** (新功能)

### 11. 交易記錄系統
- ✅ 買入/賣出記錄
- ✅ 手續費/交易稅計算
- ✅ 總金額自動計算
- ✅ 交易日期記錄
- ✅ 備註欄位
- ✅ 篩選功能 (股票代號/交易類型)
- **API端點**: `/api/v1/transactions`
- **前端組件**: `TransactionHistory.tsx`

### 12. 交易統計摘要
- ✅ 總買入金額
- ✅ 總賣出金額
- ✅ 總手續費
- ✅ 總交易稅
- ✅ 淨損益計算
- ✅ 交易筆數統計
- **API端點**: `/api/v1/transactions/summary/stats`

### 13. 持倉管理
- ✅ 當前持股列表
- ✅ 持股成本計算
- ✅ 未實現損益
- ✅ 持股比例
- ✅ 即時市值更新
- **API端點**: `/api/v1/positions`

---

## 📱 **通知整合** (新功能)

### 14. LINE Bot 通知
- ✅ 價格提醒推播
- ✅ 新聞提醒推播
- ✅ 交易記錄通知
- ✅ 自定義訊息格式
- ✅ Emoji 圖示支援
- **服務**: `LineNotifyService`
- **需要**: `LINE_NOTIFY_TOKEN` 環境變數

---

## 🎨 **前端體驗**

### 15. UI/UX 優化
- ✅ 深色主題 (Dark Mode)
- ✅ 玻璃擬態設計 (Glassmorphism)
- ✅ 流暢動畫效果
- ✅ 響應式設計 (RWD)
- ✅ 載入骨架屏 (Skeleton)
- ✅ Toast 通知

### 16. 無障礙設計
- ✅ 表單欄位 ID/Name 屬性
- ✅ Label htmlFor 關聯
- ✅ ARIA 標籤
- ✅ 鍵盤導航支援

---

## 🔧 **開發者功能**

### 17. API 文檔
- ✅ Swagger UI (`/api/docs`)
- ✅ ReDoc (`/api/redoc`)
- ✅ 自動生成 OpenAPI 規格

### 18. 數據庫管理
- ✅ Alembic 遷移系統
- ✅ 7 個遷移腳本
- ✅ 自動建表
- ✅ 索引優化

### 19. DevOps
- ✅ Docker 容器化 (4個服務)
- ✅ Docker Compose 編排
- ✅ GitHub Actions CI/CD (3個工作流)
- ✅ 代碼質量檢查
- ✅ 安全掃描 (Trivy)

---

## 🚀 **使用說明**

### 啟動所有服務
```bash
docker-compose up -d
```

### 訪問應用
- 前端: http://localhost:5173
- 後端API: http://localhost:8000
- API文檔: http://localhost:8000/api/docs

### 環境變數設定
複製 `.env.example` 為 `.env` 並設定:
```env
GEMINI_API_KEY=your_gemini_api_key
LINE_NOTIFY_TOKEN=your_line_token
```

### 測試 WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/stocks/2330.TW')
ws.onmessage = (event) => console.log(JSON.parse(event.data))
```

### 測試新聞API
```bash
# 查詢新聞
curl http://localhost:8000/api/v1/stocks/2330.TW/news?days=7

# 手動抓取
curl -X POST http://localhost:8000/api/v1/stocks/2330.TW/news/fetch
```

---

## 📈 **技術棧**

**後端**
- FastAPI 0.100+
- SQLAlchemy (Async)
- PostgreSQL 15
- Redis 7
- APScheduler
- Google Gemini AI
- feedparser
- websockets

**前端**
- React 18
- TypeScript
- Vite
- Tailwind CSS
- Recharts
- Axios
- Zustand

**DevOps**
- Docker & Docker Compose
- GitHub Actions
- Alembic
- Trivy Security Scanner

---

## 📝 **待開發功能**

- [ ] 技術分析指標 (MA, MACD, RSI)
- [ ] K線圖表
- [ ] 多因子選股
- [ ] 回測系統
- [ ] 社群討論功能
- [ ] 手機 App (React Native)

---

**版本**: v1.0.0  
**更新日期**: 2026-01-30  
**作者**: AuraTrade Team