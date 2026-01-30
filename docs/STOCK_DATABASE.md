#  股票資料庫完整支援說明

##  已完成功能

### 1. 完整股票清單
- **台灣上市 (TWSE)**: 1,078 檔
- **台灣上櫃 (TPEX)**: 11,839 檔  
- **美股**: 10 檔主流股票
- **總計**: 12,927 檔股票

### 2. 數據來源
- 台灣證交所 OpenAPI: `https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL`
- 櫃買中心 API: `https://www.tpex.org.tw/openapi/v1/tpex_mainboard_daily_close_quotes`
- Yahoo Finance (即時價格)

### 3. 搜尋功能
-  代號搜尋: `2330`  台積電
-  名稱搜尋: `台積電`  2330.TW
-  模糊搜尋: `日月光`  2311.TW
-  權證支援: 會顯示相關權證

### 4. 快取機制
- Redis 快取 24 小時
- 自動定期更新
- 首次載入約 3-5 秒

##  使用方式

### 前端搜尋
在股票搜尋框輸入任何台股代號或名稱：
- `2330`  台積電
- `2317`  鴻海
- `2454`  聯發科
- `006208`  富邦台50
- `日月光`  2311.TW

### API 端點

#### 1. 搜尋股票
`GET /api/v1/stocks/search?q=2330`

#### 2. 查看統計
`GET /api/v1/stocks/stats`

#### 3. 手動更新清單
`POST /api/v1/stocks/refresh-list`

##  技術架構

### 檔案結構
`backend/apps/core/services/stock_list_manager.py` - 股票清單管理器
`backend/apps/core/services/yahoo_finance.py` - 整合搜尋邏輯  
`backend/apps/api/v1/routes/stock.py` - API 端點

### 搜尋優先級
1. **完整股票清單** (12,927 檔) - 台灣證交所資料
2. **Yahoo Finance** - 動態查詢美股/其他市場
3. **Mock Data** - 開發測試用

##  效能優化
- Redis 快取避免重複 API 呼叫
- 非同步載入提升速度
- 搜尋結果限制 10-20 筆

##  下一步建議
1. 新增 ETF 完整清單
2. 支援港股/陸股市場
3. 建立股票資訊頁面
4. 加入產業分類篩選

---
更新時間: 2026-01-30
版本: v2.0 - 完整台股支援
