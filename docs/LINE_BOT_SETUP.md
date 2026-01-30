#  LINE Bot 通知設定指南

##  重要變更

**LINE Notify 已於 2025年3月31日停止服務**

AuraTrade 現在使用 **LINE Messaging API (LINE Bot)** 來發送通知。

---

##  快速開始

### 1. 建立 LINE Bot

前往 [LINE Developers Console](https://developers.line.biz/console/)

1. **建立 Provider**（如果還沒有）
2. **建立 Messaging API Channel**
3. 取得以下資訊：
   - **Channel Access Token** (長期 Token)
   - **Channel Secret**

### 2. 設定環境變數

編輯 `.env` 檔案：

``env
LINE_CHANNEL_ACCESS_TOKEN=your_long_lived_channel_access_token
LINE_CHANNEL_SECRET=your_channel_secret
``

### 3. 設定 Webhook URL

在 LINE Developers Console 設定：

``
https://your-domain.com/api/v1/line/webhook
``

**本地開發（需使用 ngrok）：**
``bash
ngrok http 8000
# 使用 ngrok 提供的 https URL
https://xxxxx.ngrok.io/api/v1/line/webhook
``

### 4. 啟用功能

在 LINE Developers Console：
-  啟用 **Webhook**
-  啟用 **Use webhook**
-  關閉 **Auto-reply messages**（避免重複回應）

---

##  使用流程

### 用戶端設定步驟

1. **加入 LINE Bot 為好友**
   - 掃描 QR Code 或搜尋 Bot ID

2. **發送訊息 "id" 給 Bot**
   - Bot 會回覆您的 LINE User ID

3. **登入 AuraTrade 網站**
   - 進入「設定」頁面
   - 輸入 LINE User ID
   - 啟用通知

4. **完成！**
   - 現在會收到價格提醒、新聞分析等通知

---

##  通知類型

### 1. 價格提醒
當股價突破/跌破目標價時推播：
``
 價格提醒通知

股票：台積電 (2330.TW)
當前價格：NT$ 1,050.00
目標價格：NT$ 1,000.00

您設定的價格已經突破目標價！
時間：2026-01-30 23:00:00
``

### 2. 新聞情緒分析
當有重要新聞時推播：
``
 新聞提醒

股票：台積電 (2330.TW)
利多消息（情緒分數：+0.85）

台積電Q4營收創歷史新高

時間：2026-01-30 23:00:00
``

### 3. 交易記錄
交易完成後推播：
``
 交易記錄通知

操作：買入
股票：2330.TW
數量：100 股
價格：NT$ 1,050.00
總額：NT$ 105,000.00

時間：2026-01-30 23:00:00
``

---

##  測試通知

### 方法 1: API 測試

``bash
curl "http://localhost:8000/api/v1/line/test-notification?line_user_id=YOUR_LINE_USER_ID"
``

### 方法 2: Bot 指令測試

對 Bot 發送：
- `help` - 顯示可用指令
- `status` - 查看綁定狀態
- `id` - 顯示 LINE User ID

---

##  開發者資訊

### API 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/v1/line/webhook` | POST | Webhook 接收端點 |
| `/api/v1/line/test-notification` | GET | 測試通知功能 |

### 資料庫遷移

``bash
# 執行遷移（新增 line_user_id 欄位）
cd backend
docker exec auratrade-backend alembic upgrade head
``

### 服務初始化

``python
from apps.core.services.line_service import line_bot_service

# 檢查是否設定
if line_bot_service.is_configured():
    # 發送通知
    await line_bot_service.send_price_alert(
        user_id="U1234567890abcdef",
        symbol="2330.TW",
        stock_name="台積電",
        current_price=1050.0,
        target_price=1000.0,
        condition="above"
    )
``

---

##  設定檔案

### docker-compose.yml

``yaml
environment:
  - LINE_CHANNEL_ACCESS_TOKEN=$\{LINE_CHANNEL_ACCESS_TOKEN\}
  - LINE_CHANNEL_SECRET=$\{LINE_CHANNEL_SECRET\}
``

### config.py

``python
LINE_CHANNEL_ACCESS_TOKEN: str = ""
LINE_CHANNEL_SECRET: str = ""
``

---

##  常見問題

### Q: 如何取得 LINE User ID？
**A:** 用戶加入 Bot 後，發送 `id` 指令即可取得。

### Q: 為什麼收不到通知？
**A:** 檢查以下項目：
1.  LINE Bot 已加為好友
2.  LINE User ID 正確綁定
3.  通知功能已啟用
4.  Channel Access Token 有效

### Q: 本地開發如何測試？
**A:** 使用 ngrok 建立 https tunnel：
``bash
ngrok http 8000
# 將 ngrok URL 設定到 LINE Webhook
``

### Q: LINE Notify 的舊代碼怎麼辦？
**A:** 系統已向下兼容，但建議盡快遷移：
-  `LINE_NOTIFY_TOKEN`  已無效
-  `LINE_CHANNEL_ACCESS_TOKEN`  使用新的

---

##  參考資料

- [LINE Messaging API 文檔](https://developers.line.biz/en/docs/messaging-api/)
- [LINE Bot SDK Python](https://github.com/line/line-bot-sdk-python)
- [Webhook 說明](https://developers.line.biz/en/docs/messaging-api/receiving-messages/)

---

更新時間：2026-01-30  
版本：v2.0 - LINE Bot 升級
