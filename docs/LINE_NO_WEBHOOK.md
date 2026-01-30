#  無 Webhook 模式 - 推播通知設定

##  可用功能

即使沒有 Webhook，你仍可以使用：
-  **推播價格提醒**
-  **推播新聞通知**  
-  **推播交易記錄**
-  **測試通知**

##  不可用功能

-  接收用戶訊息（需要 Webhook）
-  自動綁定（需要 Webhook）
-  互動式指令

---

##  快速設定（無 Webhook）

### 1. 建立 LINE Bot

前往 [LINE Developers Console](https://developers.line.biz/console/)

1. 建立 **Messaging API Channel**
2. 取得 **Channel Access Token**
3. **不用設定 Webhook**（可以跳過這步）

### 2. 更新 .env

``env
LINE_CHANNEL_ACCESS_TOKEN=你的_channel_access_token
# LINE_CHANNEL_SECRET 可以不設定（無 Webhook 不需要）
``

### 3. 取得 LINE User ID

**方法 1: 從 LINE Developers Console**
- 加入 Bot 為好友後
- 到 Console  Messaging API  User IDs
- 查看加入的用戶 ID

**方法 2: 使用測試工具**
- 安裝 LINE Official Account Manager APP
- 查看用戶資訊

**方法 3: 從日誌**
- 暫時啟用 Webhook（用 ngrok）
- 用戶發送訊息
- 從後端日誌查看 user_id

### 4. 手動綁定用戶

執行 SQL 或使用 API：

``sql
UPDATE users 
SET line_user_id = 'U1234567890abcdef',
    line_notify_enabled = true
WHERE email = 'your@email.com';
``

### 5. 測試推播

``bash
curl "http://localhost:8000/api/v1/line/test-notification?line_user_id=U1234567890abcdef"
``

---

##  實際使用流程

### 情境：價格提醒觸發

1. 用戶設定價格提醒（台積電 > 1000）
2. 系統監控到價格突破
3. **自動推播通知到用戶 LINE**
4. 用戶收到提醒 

### 情境：新增自選股（自動抓新聞）

1. 用戶新增自選股
2. 系統自動抓取並分析新聞
3. **發現重要新聞時推播**
4. 用戶收到新聞摘要 

---

##  開發建議

### 短期方案（無 Webhook）
- 使用推播通知功能
- 手動綁定 LINE User ID
- 在網站上提供「如何取得 LINE User ID」說明

### 長期方案（有 Webhook）
- **開發環境**: 使用 ngrok
- **正式環境**: 部署到有公開 IP 的伺服器
- 啟用完整互動功能

---

##  推薦做法

``
開發階段:
1. 先用「無 Webhook 模式」測試推播功能
2. 確認通知內容和格式正確
3. 再考慮加入 ngrok 測試互動功能

正式上線:
1. 部署到正式伺服器（有 HTTPS）
2. 設定正式 Webhook URL
3. 啟用完整功能
``

---

更新時間：2026-01-31
