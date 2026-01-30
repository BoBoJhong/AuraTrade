import httpx
from typing import Optional, List
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LineBotService:
    """
    LINE Messaging API Service for sending notifications
    ⚠️ LINE Notify 已於 2025/3/31 停止服務
    現在使用 LINE Messaging API (LINE Bot)
    """
    
    def __init__(self):
        # LINE Messaging API endpoints
        self.push_message_url = "https://api.line.me/v2/bot/message/push"
        self.broadcast_url = "https://api.line.me/v2/bot/message/broadcast"
        
        # LINE Bot Channel Access Token
        self.channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
        
        # 向下兼容：如果還有舊的 LINE_NOTIFY_TOKEN，發出警告
        old_token = os.getenv("LINE_NOTIFY_TOKEN")
        if old_token:
            logger.warning("⚠️ LINE_NOTIFY_TOKEN 已無效（服務已停止），請改用 LINE_CHANNEL_ACCESS_TOKEN")
    
    def is_configured(self) -> bool:
        """檢查 LINE Bot 是否已設定"""
        return bool(self.channel_access_token)
    
    async def send_price_alert(
        self,
        user_id: str,
        symbol: str,
        stock_name: str,
        current_price: float,
        target_price: float,
        condition: str
    ) -> bool:
        """
        發送價格提醒通知
        
        Args:
            user_id: LINE 使用者 ID（必須是已加入 Bot 的用戶）
            symbol: 股票代號
            stock_name: 股票名稱
            current_price: 當前價格
            target_price: 目標價格
            condition: 條件 ("above" 或 "below")
        """
        
        # Build message
        emoji = "🔔" if condition == "above" else "📉"
        condition_text = "突破" if condition == "above" else "跌破"
        
        message = f"""
{emoji} 價格提醒通知

股票：{stock_name} ({symbol})
當前價格：NT$ {current_price:,.2f}
目標價格：NT$ {target_price:,.2f}

您設定的價格已經{condition_text}目標價！
時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 立即查看詳情
        """.strip()
        
        return await self._send_push_message(user_id, message)
    
    async def send_news_alert(
        self,
        user_id: str,
        symbol: str,
        stock_name: str,
        news_title: str,
        sentiment: str,
        sentiment_score: float
    ) -> bool:
        """發送新聞提醒通知"""
        
        # Choose emoji based on sentiment
        if sentiment == "positive":
            emoji = "📈"
            sentiment_text = "利多消息"
        elif sentiment == "negative":
            emoji = "📉"
            sentiment_text = "利空消息"
        else:
            emoji = "📰"
            sentiment_text = "中性消息"
        
        message = f"""
{emoji} 新聞提醒

股票：{stock_name} ({symbol})
{sentiment_text}（情緒分數：{sentiment_score:+.2f}）

{news_title}

時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        return await self._send_push_message(user_id, message)
    
    async def send_transaction_notification(
        self,
        user_id: str,
        symbol: str,
        transaction_type: str,
        quantity: float,
        price: float,
        total_amount: float
    ) -> bool:
        """發送交易記錄通知"""
        
        emoji = "💰" if transaction_type == "buy" else "💸"
        action = "買入" if transaction_type == "buy" else "賣出"
        
        message = f"""
{emoji} 交易記錄通知

操作：{action}
股票：{symbol}
數量：{quantity} 股
價格：NT$ {price:,.2f}
總額：NT$ {total_amount:,.2f}

時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        return await self._send_push_message(user_id, message)
    
    async def broadcast_message(self, message: str) -> bool:
        """
        廣播訊息給所有加入 Bot 的用戶
        ⚠️ 需要 LINE 官方帳號認證才能使用
        """
        if not self.is_configured():
            logger.warning("LINE Bot 未設定 Channel Access Token")
            return False
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.channel_access_token}"
            }
            
            payload = {
                "messages": [
                    {
                        "type": "text",
                        "text": message
                    }
                ]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.broadcast_url,
                    headers=headers,
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    logger.info("✅ LINE 廣播訊息發送成功")
                    return True
                else:
                    logger.error(f"❌ LINE 廣播失敗: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ LINE 廣播錯誤: {e}")
            return False
    
    async def _send_push_message(self, user_id: str, message: str) -> bool:
        """
        發送推播訊息給特定用戶
        
        Args:
            user_id: LINE 使用者 ID（從 Webhook 事件取得）
            message: 訊息內容
        """
        if not self.is_configured():
            logger.warning("LINE Bot 未設定 Channel Access Token")
            return False
        
        if not user_id:
            logger.error("❌ user_id 不能為空")
            return False
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.channel_access_token}"
            }
            
            payload = {
                "to": user_id,
                "messages": [
                    {
                        "type": "text",
                        "text": message
                    }
                ]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.push_message_url,
                    headers=headers,
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ LINE 推播訊息發送成功 -> {user_id}")
                    return True
                else:
                    logger.error(f"❌ LINE 推播失敗: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ LINE 推播錯誤: {e}")
            return False


# Global instance (向下兼容舊變數名稱)
line_bot_service = LineBotService()
line_service = line_bot_service  # 別名，保持向下兼容