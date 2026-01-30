# AuraTrade 功能測試指南

## 🎯 **測試前準備**

### 1. 確認所有服務運行
```powershell
docker ps
```
應該看到 4 個容器:
- `auratrade-frontend` (Port 5173)
- `auratrade-backend` (Port 8000)
- `auratrade-db` (Port 5432)
- `auratrade-redis` (Port 6379)

### 2. 檢查後端健康狀態
```powershell
curl http://localhost:8000/health
```

### 3. 開啟瀏覽器開發者工具
- 按 `F12`
- 切換到 **Network** 分頁
- 勾選 **Disable cache**

---

## ✅ **功能測試清單**

### 🔐 **1. 認證系統測試**

#### 測試註冊
1. 訪問 http://localhost:5173
2. 點擊「註冊」
3. 填寫 Email 和密碼
4. 點擊提交
5. **預期**: 顯示「註冊成功」並自動登入

#### 測試登入
1. 點擊「登出」(如果已登入)
2. 點擊「登入」
3. 輸入正確帳密
4. **預期**: 成功登入並跳轉到儀表板

---

### 📊 **2. 股票查詢測試**

#### 測試台股查詢
1. 在搜尋欄輸入 `2330.TW`
2. 按 Enter
3. **預期**: 顯示台積電股票詳情頁
4. **檢查**: 
   - ✅ 股價顯示
   - ✅ 漲跌幅計算 (不是固定 +0.00)
   - ✅ 歷史圖表顯示
   - ✅ 5d/1mo/3mo/1y 切換正常

#### 測試美股查詢
1. 搜尋 `AAPL`
2. **預期**: 顯示 Apple 股票資訊

---

### ⭐ **3. 自選股測試**

#### 測試新增自選股
1. 搜尋 `2330.TW`
2. 點擊「加入自選」按鈕
3. **預期**: 按鈕變為「已加入」
4. 返回首頁
5. **檢查**: 自選股列表出現台積電

#### 測試價格顯示
1. 在自選股列表
2. **檢查**:
   - ✅ 當前價格顯示
   - ✅ 漲跌數字顯示 (不是 +0.00)
   - ✅ 漲跌百分比顯示
   - ✅ 顏色正確 (紅漲/綠跌)

#### 測試展開圖表
1. 點擊自選股卡片
2. **預期**: 卡片展開顯示歷史圖表
3. 再次點擊
4. **預期**: 圖表收起

#### 測試移除自選股
1. 點擊垃圾桶圖示
2. **預期**: 自選股從列表移除

---

### 🔔 **4. 價格提醒測試**

#### 測試設定提醒
1. 在自選股卡片點擊鈴鐺圖示
2. 填寫目標價格 (例如: 1800)
3. 選擇「突破」或「跌破」
4. 點擊「設定」
5. **預期**: 提醒設定成功

#### 測試提醒列表
1. API 測試:
```powershell
$token = "your_jwt_token"
curl -H "Authorization: Bearer $token" http://localhost:8000/api/v1/alerts
```
2. **預期**: 返回提醒列表

---

### 📰 **5. 新聞系統測試 (新功能)**

#### 測試新聞顯示
1. 前往股票詳情頁 (例如 2330.TW)
2. 滾動到新聞面板
3. **檢查**:
   - ✅ 新聞列表顯示
   - ✅ 情緒標籤 (📈利多/📉利空/➡️中性)
   - ✅ 時間顯示 (X小時前)
   - ✅ 來源顯示

#### 測試時間篩選
1. 點擊「1天」/「7天」/「30天」按鈕
2. **預期**: 新聞列表根據時間範圍更新

#### 測試手動更新
1. 點擊「更新新聞」按鈕
2. **預期**: 按鈕顯示「抓取中...」
3. 等待完成
4. **預期**: 新聞列表更新

#### API 測試
```powershell
# 查詢新聞
curl "http://localhost:8000/api/v1/stocks/2330.TW/news?days=7&limit=10"

# 手動抓取
curl -X POST "http://localhost:8000/api/v1/stocks/2330.TW/news/fetch"
```

---

### ⚡ **6. WebSocket 實時更新測試 (新功能)**

#### 瀏覽器測試
1. 打開瀏覽器開發者工具 (F12)
2. 切換到 **Console** 分頁
3. 執行:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/stocks/2330.TW')
ws.onopen = () => console.log('✅ WebSocket 連線成功')
ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    console.log('📊 價格更新:', data)
}
ws.onerror = (error) => console.error('❌ 錯誤:', error)
```

4. **預期**: 
   - 每 5 秒收到價格更新
   - 包含 symbol, price, change, change_percent

#### 使用 React Hook
1. 在股票詳情頁
2. 打開開發者工具 Network → WS
3. **檢查**: WebSocket 連線狀態
4. **預期**: 價格即時更新

---

### 💼 **7. 交易記錄測試 (新功能)**

#### 測試新增交易
```powershell
$token = "your_jwt_token"
$body = @{
    stock_symbol = "2330.TW"
    transaction_type = "buy"
    quantity = 10
    price = 600
    commission = 42
    tax = 0
    transaction_date = "2026-01-30"
    notes = "測試買入"
} | ConvertTo-Json

curl -X POST "http://localhost:8000/api/v1/transactions" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d $body
```

#### 測試查詢交易
```powershell
curl -H "Authorization: Bearer $token" "http://localhost:8000/api/v1/transactions"
```

#### 測試交易統計
```powershell
curl -H "Authorization: Bearer $token" "http://localhost:8000/api/v1/transactions/summary/stats"
```

#### 前端測試
1. 訪問交易記錄頁面 (如果有路由)
2. **檢查**:
   - ✅ 統計卡片顯示 (總買入/總賣出/淨損益)
   - ✅ 交易列表顯示
   - ✅ 篩選功能 (股票代號/類型)
   - ✅ 刪除按鈕

---

### 📱 **8. LINE 通知測試 (新功能)**

#### 設定 LINE Notify Token
1. 訪問 https://notify-bot.line.me/
2. 登入 LINE 帳號
3. 點擊「個人頁面」→「發行權杖」
4. 選擇接收通知的聊天室
5. 複製 Token

#### 配置環境變數
```env
# backend/.env
LINE_NOTIFY_TOKEN=your_token_here
```

#### 測試價格提醒通知
1. 設定一個容易觸發的價格提醒
2. 等待後端檢查 (每分鐘)
3. **預期**: LINE 收到通知

#### 手動測試
```python
# 在後端容器內執行
docker exec -it auratrade-backend python -c "
from apps.core.services.line_service import line_service
import asyncio
asyncio.run(line_service.send_price_alert(
    symbol='2330.TW',
    stock_name='台積電',
    current_price=1850.0,
    target_price=1800.0,
    condition='above'
))
"
```

---

## 🐛 **常見問題排查**

### 問題 1: 前端無法連接後端
**症狀**: API 請求失敗，Console 顯示 CORS 錯誤

**解決**:
```powershell
# 檢查後端是否運行
docker logs auratrade-backend --tail 20

# 檢查CORS設定
curl -H "Origin: http://localhost:5173" http://localhost:8000/health -v
```

### 問題 2: WebSocket 連線失敗
**症狀**: ws://localhost:8000/api/v1/ws/stocks/... 無法連接

**解決**:
```powershell
# 檢查後端 WebSocket 路由
curl http://localhost:8000/api/docs
# 搜尋 "websocket"

# 重啟後端
docker-compose restart backend
```

### 問題 3: 新聞不顯示
**症狀**: 新聞列表為空

**解決**:
```powershell
# 檢查是否有新聞數據
docker exec -it auratrade-backend psql -U postgres -d auratrade -c "SELECT COUNT(*) FROM stock_news;"

# 手動觸發新聞抓取
curl -X POST "http://localhost:8000/api/v1/stocks/2330.TW/news/fetch"

# 檢查排程器日誌
docker logs auratrade-backend | Select-String "News"
```

### 問題 4: Gemini AI 分析失敗
**症狀**: 新聞沒有情緒標籤

**檢查**:
1. 確認 `GEMINI_API_KEY` 已設定
2. 檢查 API 配額
3. 查看後端日誌:
```powershell
docker logs auratrade-backend | Select-String "Gemini"
```

---

## 📊 **性能測試**

### 測試 API 響應時間
```powershell
Measure-Command { curl http://localhost:8000/api/v1/stocks/2330.TW/quote }
```
**預期**: < 2 秒

### 測試 WebSocket 延遲
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/stocks/2330.TW')
ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    const now = Date.now()
    const serverTime = new Date(data.timestamp).getTime()
    console.log(`延遲: ${now - serverTime}ms`)
}
```

---

## ✨ **測試完成確認**

所有功能測試通過後，你應該能夠:

- [x] 註冊/登入成功
- [x] 查詢台股/美股
- [x] 新增/移除自選股
- [x] 看到正確的價格漲跌
- [x] 設定價格提醒
- [x] 查看股票新聞與 AI 情緒分析
- [x] WebSocket 即時價格更新
- [x] 記錄買賣交易
- [x] 查看交易統計
- [x] 收到 LINE 通知 (如果已設定)

**恭喜！AuraTrade 已經可以正常運行！** 🎉

---

**測試報告模板**:
```
測試日期: 2026-01-30
測試人員: [你的名字]
瀏覽器: Chrome 120 / Firefox 121
OS: Windows 11 / macOS 14

功能          | 狀態 | 備註
-------------|------|------
認證系統      | ✅   | 
股票查詢      | ✅   | 
自選股管理    | ✅   | 
價格提醒      | ✅   | 
新聞系統      | ✅   | 
WebSocket     | ✅   | 
交易記錄      | ✅   | 
LINE通知      | ⏸️   | 未設定Token
```