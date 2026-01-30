# AuraTrade 變更日誌

本文檔記錄所有重要的專案變更。

格式基於 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)，
版本號遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

---

## [Unreleased]

### 🔥 最新更新 (2026-01-30 下午)

#### 🐛 修復漲跌數據顯示 Bug
- **問題**: StockDetailPage 右側顯示固定的 +0.00 (+0.00%)
- **根本原因**: Yahoo Finance API 返回的 change/change_percent 可能為 null (盤後時間)
- **解決方案**: 
  - 修改 `get_stock_quote()` 函數,當漲跌數據為空時自動從歷史數據計算
  - 計算邏輯: change = 今日收盤 - 昨日收盤
  - 確保台股盤後也能顯示正確漲跌
- **修改檔案**:
  - `backend/apps/api/v1/routes/stock.py` (Line 54-96)
  - `frontend/src/pages/stock/StockDetailPage.tsx` (Line 92-108)
- **效果**: ✅ 漲跌數字正確顯示,紅色↑上漲/綠色↓下跌

#### 🎯 AI 推薦 API 完整實作
- **RecommendationEngine 推薦引擎**:
  - 技術指標分析 (40%): RSI、MACD、MA
  - 基本面分析 (40%): 本益比、殖利率、股價淨值比
  - 新聞情緒分析 (20%): Alpha Vantage 情緒 API (僅美股)
- **API 端點**: `GET /api/v1/recommendations?market=TW&limit=10`
- **候選股票池**: 台股15檔 + 美股15檔
- **新增檔案**: `backend/apps/api/v1/routes/recommendations.py` (343行)
- **前端整合**: RecommendedStocks 組件改用真實 API,移除 Mock 數據

### 進行中

- [x] Fugle API 整合（台股即時行情）✅
- [x] Alpha Vantage API 整合（美股 + 技術指標）✅
- [x] AI 推薦引擎 ✅
- [ ] 新聞爬蟲系統
- [ ] LINE Bot 通知功能

### 規劃中

- [ ] 推薦結果 Redis 快取優化
- [ ] TWSE 法人買賣超數據解析
- [ ] 五檔報價顯示
- [ ] WebSocket 即時推送
- [ ] iOS / Android 原生應用
- [ ] 多語言支援 (i18n)

---

## [0.7.0] - 2026-01-30

### Added - 新增功能

#### Alpha Vantage API 整合（美股 + 技術指標）

- ✅ **Alpha Vantage Service 整合**
  - 實作 `AlphaVantageService` 服務類別
  - 支援美股即時報價與歷史數據查詢
  - 60+ 技術指標 API 支援
  - 新聞情緒分析功能
  - 自動偵測 API 可用性

- ✅ **AlphaVantageService 核心功能**
  - `get_quote()` - 美股即時報價（GLOBAL_QUOTE）
  - `get_daily_data()` - 歷史數據（compact: 100天 / full: 20年）
  - `get_technical_indicator()` - 技術指標（SMA, EMA, MACD, RSI, BBANDS 等）
  - `get_news_sentiment()` - 新聞情緒分析（可用於 AI 推薦）

- ✅ **環境變數設定**
  - 新增 `ALPHA_VANTAGE_API_KEY` 設定於 `config.py`
  - 更新 `.env` 模板檔案

#### Fugle API 整合（台股即時行情）

- ✅ **Fugle MarketData SDK 整合**
  - 新增 `fugle-marketdata==1.0.1` 套件
  - 實作 `FugleService` 服務類別
  - 支援台股即時報價與歷史數據查詢
  - 自動偵測 API 可用性

- ✅ **FugleService 核心功能**
  - `get_intraday_ticker()` - 個股即時報價（價格、漲跌、成交量）
  - `get_intraday_candles()` - 盤中 K 線數據
  - `get_historical_candles()` - 歷史 K 線數據（預設 90 天）
  - `get_quote()` - 完整報價（含五檔、內外盤）
  - `_normalize_symbol()` - 自動處理 .TW/.TWO 後綴

- ✅ **數據源優先級優化（完整版）**
  - **台股盤中** (09:00-13:30)：**Fugle** → Yahoo Finance → TWSE → FinMind → Mock
  - **台股盤後**：TWSE → FinMind → Fugle → Yahoo Finance → Mock
  - **美股**：**Alpha Vantage** → Yahoo Finance → Mock
  - 原因：
    - Fugle 提供真正的台股即時報價（延遲 < 1 秒）
    - Alpha Vantage 提供美股即時報價（無 429 限流）
    - 解決 Yahoo Finance 限流問題

- ✅ **環境變數設定**
  - 新增 `FUGLE_API_KEY` 設定於 `config.py`
  - 建立 `.env` 模板檔案
  - 支援動態 API Key 載入

### Changed - 變更

- 升級數據源策略，台股盤中優先使用 Fugle API，美股優先使用 Alpha Vantage
- `get_historical_data()` 支援 Fugle 歷史 K 線查詢（台股）與 Alpha Vantage 歷史數據查詢（美股）
- 多數據源架構擴展為 7 層備援（DB Cache → 專用 API → Yahoo Finance → Web Scraper → Mock）

### Technical - 技術細節

**後端架構更新**
```
apps/
  core/
    services/
      fugle_service.py (新增 - 台股)
      alpha_vantage_service.py (新增 - 美股)
      yahoo_finance.py (更新數據源策略)
    config.py (新增 FUGLE_API_KEY + ALPHA_VANTAGE_API_KEY)
.env (新增兩組 API Key)
```

**完整數據源流程圖**
```
查詢流程：
├─ 台股 (.TW/.TWO)
│  ├─ Redis Cache (60s TTL)
│  │  ↓ miss
│  ├─ 盤中 (09:00-13:30)
│  │  ├─ Fugle API ⭐ (即時，延遲<1s)
│  │  ├─ Yahoo Finance (備援)
│  │  └─ TWSE OpenAPI (最終備援)
│  └─ 盤後
│     ├─ TWSE OpenAPI (精確收盤價)
│     ├─ FinMind (備援)
│     ├─ Fugle API
│     └─ Yahoo Finance (最終備援)
│
└─ 美股 (AAPL, MSFT, etc.)
   ├─ Redis Cache (60s TTL)
   │  ↓ miss
   ├─ Alpha Vantage ⭐ (即時報價，免費 25 req/day)
   ├─ Yahoo Finance (備援)
   └─ Mock Data (開發測試)
```

**API 使用範例**
```python
# ===== Fugle API (台股) =====
from apps.core.services.fugle_service import fugle_service

# 即時報價
ticker = await fugle_service.get_intraday_ticker("2330.TW")
# {'symbol': '2330', 'price': 625.0, 'change': 5.0}

# 歷史數據
candles = await fugle_service.get_historical_candles(
    "2330.TW",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# ===== Alpha Vantage API (美股) =====
from apps.core.services.alpha_vantage_service import alpha_vantage_service

# 即時報價
quote = await alpha_vantage_service.get_quote("AAPL")
# {'symbol': 'AAPL', 'price': 185.5, 'changePercent': 1.26}

# 歷史數據
history = await alpha_vantage_service.get_daily_data("AAPL", outputsize='compact')

# 技術指標
rsi = await alpha_vantage_service.get_technical_indicator(
    "AAPL", 
    indicator="RSI", 
    time_period=14
)

# 新聞情緒
news = await alpha_vantage_service.get_news_sentiment(tickers="AAPL,MSFT")
```

### Benefits - 效益

- ✅ **解決 Yahoo Finance 429 限流問題**
- ✅ **台股即時數據更準確**（延遲 < 1 秒）
- ✅ **完整 OHLCV 數據**（無需前端模擬）
- ✅ **支援盤中 K 線**（1/5/15/30/60 分鐘）
- ✅ **五檔報價支援**（未來可擴展）

### Next Steps - 後續步驟

1. **設定 API Key**：在 `.env` 填入 `FUGLE_API_KEY=your_api_key`
2. **重啟後端**：`docker-compose restart backend`
3. **測試台股查詢**：查詢 2330.TW 驗證 Fugle 數據
4. **前端整合**：確認 WatchlistCard/PositionCard 顯示正確價格
5. **未來擴展**：整合五檔報價顯示、盤中推播

---

## [0.6.0] - 2026-01-30

### Added - 新增功能

#### TWSE OpenAPI 整合

- ✅ **升級 TWSE Service 使用 OpenAPI v1**
  - 新增 `OPENAPI_BASE_URL` (openapi.twse.com.tw/v1)
  - 整合官方 OpenAPI 數據源
  - 實作基本面數據查詢方法
  
- ✅ **基本面分析功能**
  - `get_fundamental_data()` - 查詢本益比、殖利率、股價淨值比
  - 使用 TWSE OpenAPI `/exchangeReport/BWIBBU_ALL`
  - 支援所有上市股票基本面資料
  
- ✅ **股利資訊查詢**
  - `get_dividend_info()` - 查詢現金股利、股票股利、除息日
  - 使用 TWSE OpenAPI `/opendata/t187ap45_L`
  - 顯示最新股利分派資訊
  
- ✅ **法人買賣超功能（架構完成）**
  - `get_institutional_investors()` - 查詢三大法人動態
  - 支援外資、投信、自營商買賣超
  - API 端點預留，待實際數據格式確認

#### Market API 路由

- ✅ **新增 Market API Router**
  - `GET /api/v1/market/fundamental/{symbol}` - 基本面資料
  - `GET /api/v1/market/dividend/{symbol}` - 股利資訊
  - `GET /api/v1/market/institutional` - 法人買賣超
  - `GET /api/v1/market/stock-info/{symbol}` - 綜合資訊（一次取得所有數據）
  - 統一錯誤處理與日誌記錄

#### 前端市場資料服務

- ✅ **marketService.ts 服務層**
  - TypeScript 完整型別定義
  - `FundamentalData` 介面（本益比、殖利率、股價淨值比）
  - `DividendInfo` 介面（現金股利、股票股利、除息日）
  - `InstitutionalData` 介面（法人買賣超）
  - `ComprehensiveStockInfo` 綜合資訊介面
  - 4 個 API 調用方法

#### 股票詳情頁面

- ✅ **StockDetailPage 完整分析頁面**
  - 響應式三欄佈局（基本面 + 股利 + 圖表）
  - 股票標題區（價格、推薦、評分）
  - 基本面分析卡片（P/E, Dividend Yield, P/B）
  - 股利資訊卡片（現金股利、股票股利、除息日）
  - 技術分析詳情卡片（9 項指標詳情）
  - 完整圖表組（K 線、成交量、MACD、RSI）
  - 毛玻璃風格設計，與系統一致

#### 導航功能增強

- ✅ **WatchlistCard 新增詳情按鈕**
  - 藍色「查看完整分析」按鈕
  - 點擊跳轉至 `/stock/:symbol`
  - React Router 導航整合
  
- ✅ **App.tsx 路由更新**
  - 新增 `/stock/:symbol` 路由
  - 受保護路由（需登入）
  - 動態參數傳遞

### Changed - 變更

- 升級 TWSE Service 支援 OpenAPI v1 端點
- main.py 註冊 market router

### Technical - 技術細節

**後端架構**
```
apps/
  core/
    services/
      twse_service.py (升級支援 OpenAPI)
  api/
    v1/
      routes/
        market.py (新)
```

**前端架構**
```
src/
  services/
    marketService.ts (新)
  pages/
    stock/
      StockDetailPage.tsx (新)
  components/
    stocks/
      WatchlistCard.tsx (更新)
  App.tsx (更新)
```

**API 端點新增**
- GET /api/v1/market/fundamental/{symbol}
- GET /api/v1/market/dividend/{symbol}
- GET /api/v1/market/institutional
- GET /api/v1/market/stock-info/{symbol}

**頁面路由新增**
- /stock/:symbol (StockDetailPage)

---

## [0.3.0] - 2026-01-30

### Added - 新增功能

#### 多數據源策略 (REQ-003, US-03)

- ✅ **6 層數據源備援架構**
  - **第 1 層**: PostgreSQL 資料庫快取（3 天有效期，80% 完整度檢查）
  - **第 2 層**: TWSE 台灣證券交易所官方 API（台股優先）
  - **第 3 層**: FinMind 金融數據平台 API（台股備援）
  - **第 4 層**: Yahoo Finance API（全球股市）
  - **第 5 層**: Yahoo Finance CSV 網頁爬蟲
  - **第 6 層**: Mock 數據（開發測試用）
  
- ✅ **TWSE 官方 API 服務**
  - 實作 `TWSEService` 類別
  - 支援個股日成交資訊查詢
  - 自動處理台股代碼格式（移除 .TW/.TWO 後綴）
  - 返回標準 OHLCV 格式數據
  - 錯誤處理與日誌記錄
  
- ✅ **FinMind API 服務**
  - 實作 `FinMindService` 類別
  - 台股日線數據查詢
  - 股票基本資訊查詢
  - 日期範圍查詢支援
  
- ✅ **歷史價格資料庫快取**
  - 新增 `historical_prices` 資料表
  - 欄位：symbol, date, open, high, low, close, volume
  - 索引：symbol+date 唯一索引、symbol+date 範圍查詢索引
  - 自動儲存外部 API 數據到快取
  - 智能快取驗證（3 天內且 80% 完整）

#### 技術指標圖表系統 (REQ-004, US-03)

- ✅ **K 線圖（蠟燭圖）**
  - 自定義 `Candlestick` React 組件
  - OHLC 數據視覺化（開盤、最高、最低、收盤）
  - 紅色蠟燭：收盤價 > 開盤價（上漲）
  - 綠色蠟燭：收盤價 < 開盤價（下跌）
  - 上下影線顯示最高/最低價
  - Doji 處理（開盤價=收盤價時顯示十字線）
  - 自動模擬 OHLC（當後端僅返回 price 時）
  
- ✅ **MA 移動平均線**
  - 支援 MA5（5日）、MA10（10日）、MA20（20日）、MA60（60日）
  - 獨立切換按鈕控制顯示/隱藏
  - 不同顏色區分：藍色（MA5）、黃色（MA10）、粉色（MA20）、綠色（MA60）
  - 虛線樣式便於與 K 線區分
  
- ✅ **MACD 指標子圖表**
  - ComposedChart 組合圖表（柱狀圖 + 折線圖）
  - Histogram 柱狀圖：正值紅色、負值綠色
  - MACD 線：藍色（快線）
  - Signal 線：黃色（慢線）
  - 0 軸參考線（灰色虛線）
  - Y 軸自動縮放
  
- ✅ **RSI 相對強弱指標子圖表**
  - AreaChart 區域圖
  - 紫色 RSI 線 + 漸變填充效果
  - Y 軸範圍：0-100 固定
  - 超買參考線：70（紅色虛線）
  - 超賣參考線：30（綠色虛線）
  - 參考線標籤顯示
  
- ✅ **KDJ 隨機指標子圖表**
  - LineChart 多線圖表
  - K 線：藍色（快速隨機指標）
  - D 線：橙色（慢速隨機指標）
  - J 線：紫色（超前指標）
  - Y 軸範圍：0-100 固定
  - 超買參考線：80（紅色虛線）
  - 超賣參考線：20（綠色虛線）
  
- ✅ **技術指標計算服務**
  - 實作 `TechnicalIndicatorService` 類別
  - MA 計算（pandas rolling mean）
  - MACD 計算（EMA + Signal + Histogram）
  - RSI 計算（14 期相對強弱）
  - KDJ 計算（Stochastic Oscillator）
  - 統一 API：`GET /api/v1/stocks/{symbol}/indicators`

#### 圖表增強功能

- ✅ **時間週期選擇器**
  - 支援：1日、5日、1月、3月、1年
  - 按鈕式切換（響應式設計）
  - 自動重新載入圖表數據
  
- ✅ **互動式圖表**
  - Recharts 圖表庫整合
  - 懸浮提示框（Tooltip）顯示詳細數據
  - 響應式容器適配各種螢幕
  - 圖例標籤（Legend）
  - 網格線（CartesianGrid）
  
- ✅ **數據來源資訊**
  - 圖表底部顯示數據來源
  - 顯示最後更新時間（本地化格式）
  
- ✅ **自動降級機制**
  - 當後端無 OHLC 數據時，前端自動模擬
  - open = close × 0.995
  - high = close × 1.005
  - low = close × 0.995

### Changed - 變更

#### 後端優化

- ✅ **歷史數據 API 重構**
  - `get_historical_data()` 改為 async 函數
  - 支援資料庫 session 參數（啟用快取）
  - 智能數據源選擇（台股/美股不同策略）
  - 交易時段檢測（台股 09:00-13:30）
  - 日誌增強（每層數據源成功/失敗記錄）
  
- ✅ **Mock 數據生成改進**
  - `_get_mock_historical_data()` 生成完整 OHLC
  - 模擬真實價格波動（-3% ~ +3%）
  - 隨機成交量（1000萬 ~ 5000萬）
  - 測試數據：2330.TW 42 筆記錄（$1410 → $1805）

#### 前端優化

- ✅ **StockChart 組件重構**
  - 從 LineChart 升級為 ComposedChart（支援混合圖表）
  - 新增 ChartData interface（擴展 OHLC 欄位）
  - 數據合併邏輯優化（歷史數據 + 技術指標）
  - 控制台調試日誌（📊 歷史數據、📈 技術指標、✅ 合併後數據）
  
- ✅ **WatchlistCard 組件改進**
  - 展開/收起動畫優化
  - 圖表載入狀態提示
  - 錯誤處理與顯示

### Fixed - 修復

- ✅ **語法錯誤修復**
  - 修復 StockChart.tsx 數據合併邏輯錯誤
  - 修復 MA60 Line 組件未正確關閉
  - 修復 MACD 註釋格式錯誤
  
- ✅ **蠟燭圖渲染問題**
  - 修復全綠蠟燭問題（OHLC 數據缺失）
  - 改進座標計算邏輯（從 payload 取得數據）
  - 增加蠟燭寬度（至少 2px，60% 可用寬度）
  - 添加 null/undefined 檢查
  
- ✅ **容器重啟策略**
  - 確立 Docker + Vite HMR 限制
  - 代碼變更後需執行 `docker-compose restart frontend`
  - 瀏覽器需強制刷新（Ctrl+Shift+R）

### Technical Debt - 技術債

- ⚠️ **Yahoo Finance Rate Limiting**
  - 當前遭遇 429 Too Many Requests 錯誤
  - 臨時方案：使用 Mock 數據開發
  - 計畫方案：IP 輪換、代理服務器、等待解封（1-24 小時）
  
- ⚠️ **Future Date Issue**
  - 系統日期設為 2026-01-30（未來日期）
  - 導致 TWSE/FinMind API 返回 400（數據不存在）
  - 不影響開發，Mock 數據足夠測試使用

### Testing - 測試

- ✅ **功能測試完成**
  - 多數據源策略：DB Cache ✅ → TWSE ✅ → FinMind ⚠️ → Yahoo ⚠️ → Mock ✅
  - K 線圖顯示：紅綠蠟燭正常 ✅
  - MA 線切換：MA5/10/20/60 ✅
  - MACD 子圖表：Histogram + 雙線 ✅
  - RSI 子圖表：區域圖 + 參考線 ✅
  - KDJ 子圖表：三線 + 參考線 ✅
  - 時間週期切換：1d/5d/1mo/3mo/1y ✅
  
- ✅ **整合測試**
  - 前後端數據流測試 ✅
  - 圖表響應式測試 ✅
  - 容器重啟測試 ✅

### Documentation - 文件

- ✅ **代碼註釋**
  - Candlestick 組件詳細註釋
  - 數據源策略流程註釋
  - API 參數說明
  
- ✅ **CHANGELOG 更新**
  - v0.3.0 完整變更記錄
  - 功能清單與測試結果

---

## [0.2.0] - 2026-01-30

### Added - 新增功能

#### 後端 API 實作

- ✅ **用戶認證系統 (REQ-012, REQ-013)**
  - 用戶註冊 API (`POST /api/v1/auth/register`)
  - 用戶登入 API (`POST /api/v1/auth/login`)
  - JWT Token 認證機制
  - BCrypt 密碼雜湊（直接使用 bcrypt 而非 passlib）
  - Token payload 標準化（使用 `sub` 欄位）
  
- ✅ **用戶資訊 API (REQ-014)**
  - 獲取當前用戶資訊 (`GET /api/v1/auth/me`)
  - JWT Bearer Token 驗證中介軟體
  
- ✅ **股票搜尋功能 (REQ-001, US-01)**
  - 股票搜尋 API (`GET /api/v1/stocks/search?q={query}`)
  - 智能股票代碼識別：
    - 支援直接輸入台股代碼（如 `2330` 自動轉換為 `2330.TW`）
    - 支援美股代碼（如 `AAPL`, `MSFT`）
    - 自動嘗試 `.TW` 和 `.TWO`（上市/上櫃）
  - Yahoo Finance API 整合
  - Redis 快取機制（股票資訊 TTL: 1 小時，價格 TTL: 60 秒）
  
- ✅ **自選股管理 (REQ-002, US-02)**
  - 獲取自選股列表 (`GET /api/v1/watchlist`)
  - 新增股票到自選股 (`POST /api/v1/watchlist`)
  - 從自選股移除 (`DELETE /api/v1/watchlist/{symbol}`)
  - 即時價格更新整合
  
- ✅ **股票詳情 API (REQ-003)**
  - 獲取單一股票資訊 (`GET /api/v1/stocks/{symbol}`)

#### 資料庫 Schema

- ✅ **Users Table (REQ-088)**
  - UUID 主鍵
  - Email 唯一索引
  - BCrypt 密碼雜湊
  - 用戶角色 (user/admin)
  - 帳號啟用狀態
  
- ✅ **Stocks Table (REQ-089)**
  - 股票代碼主鍵
  - 股票名稱、市場、產業分類
  
- ✅ **Watchlists Table (REQ-090)**
  - UUID 主鍵
  - 用戶 ID 外鍵 (UUID)
  - 股票代碼外鍵
  - 目標價格設定
  - 建立時間戳記

#### 前端實作

- ✅ **認證頁面 (US-12)**
  - 登入頁面 (`/login`) - Glassmorphic 設計
  - 註冊頁面 (`/register`) - 現代化 UI
  - 表單驗證與錯誤提示
  - 登入成功自動跳轉至 Dashboard
  
- ✅ **Dashboard 主頁 (US-01)**
  - 響應式 Navbar（品牌、搜尋、用戶選單）
  - 用戶資訊顯示
  - 登出功能
  
- ✅ **股票搜尋組件 (US-02)**
  - 即時搜尋（輸入後 500ms 自動搜尋）
  - 智能股票代碼提示
  - 美化的搜尋結果顯示：
    - 股票代碼、名稱、市場標籤
    - 當前價格、漲跌幅
    - 產業分類
    - Hover 動畫效果
  - 載入動畫與清除按鈕
  - 找不到結果的友善提示
  
- ✅ **自選股卡片 (US-02)**
  - 自選股列表顯示
  - 即時價格更新
  - 刪除功能

- ✅ **UI 組件庫**
  - Button 組件（漸層效果、載入狀態）
  - Input 組件（Focus 動畫、錯誤狀態）
  - Glassmorphic 布局組件

#### 架構與基礎設施

- ✅ **JWT 認證系統 (REQ-014)**
  - Access Token (15 分鐘有效期)
  - Refresh Token (7 天有效期)
  - HTTPBearer Token 驗證
  - 自動 Token 附加 (Axios Interceptor)
  
- ✅ **依賴注入 (dependencies.py)**
  - `get_current_user` - JWT Token 解析與用戶驗證
  - `get_db` - 資料庫連線管理
  
- ✅ **Zustand 狀態管理**
  - Auth Store（用戶狀態、Token 管理）
  - LocalStorage 持久化

- ✅ **Docker 容器化**
  - Frontend (Vite Dev Server - Port 5173)
  - Backend (FastAPI + Uvicorn - Port 8000)
  - PostgreSQL 15 (Port 5432)
  - Redis 7 (Port 6379)
  - Volume 掛載支援熱重載

### Fixed - 修復問題

- ✅ 修復 Tailwind CSS v4 配置問題（PostCSS 插件）
- ✅ 修復前端 Axios 導入錯誤（default → named export）
- ✅ 修復 Vite proxy 配置（localhost → container name）
- ✅ 修復 Watchlist UUID 類型不匹配
- ✅ 修復 BCrypt 密碼雜湊 72-byte 限制問題
- ✅ 修復 JWT Token payload 欄位命名（`user_id` → `sub`）
- ✅ 修復所有路由中的 `current_user.id` → `current_user.user_id`
- ✅ 修復 `get_current_user` 導入路徑錯誤

### Changed - 變更

- ✅ 移除 passlib CryptContext，直接使用 bcrypt 函式庫
- ✅ 優化 Yahoo Finance 搜尋邏輯（智能代碼識別）
- ✅ 改善前端搜尋 UX（即時搜尋、清除按鈕、載入動畫）
- ✅ 更新 Auth Store 以支援後端扁平化回應結構

### Security - 安全性

- ✅ 密碼雜湊使用 BCrypt (12 rounds)
- ✅ JWT Token 驗證與過期處理
- ✅ CORS 配置（允許 localhost:5173）
- ✅ 密碼長度自動截斷至 72 bytes

### Documentation - 文檔

- ✅ 更新 CHANGELOG.md（本次更新）
- ⏳ 待更新：PRD、SRS、SDD 以反映實際實作

### Testing - 測試

- ✅ 完整 API 測試腳本 (`test_full_api.ps1`)
  - 用戶註冊/登入測試
  - JWT 認證測試
  - 股票搜尋測試
  - 自選股 CRUD 測試
- ✅ 股票搜尋專項測試 (`test_stock_search.ps1`)

### Known Issues - 已知問題

- ⚠️ Yahoo Finance API 限流問題（429 Too Many Requests）
  - 影響：頻繁測試時無法獲取股票資訊
  - 解決方案：等待 5-10 分鐘或實作本地快取/模擬資料
- ⚠️ 前端登入跳轉需手動清除 localStorage
  - 影響：首次登入可能不跳轉
  - 解決方案：清除瀏覽器快取後重新登入

---

## [0.1.0] - 2026-01-29

### Added - 新增功能

- ✅ 完整的專案規範體系
  - 文件驅動開發規範 (rules.md v3.0)
  - PRD / SRS / SDD / API / DB_SCHEMA 文檔模板
  - 安全規範 (SECURITY.md)
  - 錯誤處理規範 (ERROR_HANDLING.md)
  - 環境設置指南 (ENVIRONMENT_SETUP.md)
  - 監控規範 (MONITORING.md)
  - 部署指南 (DEPLOYMENT.md)
  - 系統架構文檔 (ARCHITECTURE.md)

- ✅ 7 個 AI Skills 工具
  - DDD Architecture Guardian
  - Spec-to-Test Generator
  - Doc-Code Sync Validator
  - API Contract Validator
  - Migration Generator
  - Component Generator
  - Requirement Tracer

- ✅ 完整的測試規範
  - TDD 開發流程
  - 單元測試 / 整合測試 / E2E 測試標準
  - 測試覆蓋率要求 (≥70%)
  - 測試金字塔原則

- ✅ 專案資料夾架構
  - 前端 (React + TypeScript + Vite)
  - 後端 (FastAPI + PostgreSQL)
  - 每個資料夾都含 README.MD

- ✅ 團隊協作規範
  - Git Commit 訊息規範
  - Pull Request 模板
  - 貢獻者指南 (CONTRIBUTING.md)

### 文檔版本歷史

- rules.md: v1.0 → v2.0 → v3.0
- 新增 10+ 核心文檔

---

## 版本說明

### 版本號格式: MAJOR.MINOR.PATCH

- **MAJOR**: 重大架構變更或不兼容的 API 變更
- **MINOR**: 新增功能但向後兼容
- **PATCH**: Bug 修復或小更新

---

## 變更類型

- **Added**: 新增功能
- **Changed**: 現有功能的變更
- **Deprecated**: 即將移除的功能
- **Removed**: 已移除的功能
- **Fixed**: Bug 修復
- **Security**: 安全性相關變更

---

**維護者**: AuraTrade Development Team
