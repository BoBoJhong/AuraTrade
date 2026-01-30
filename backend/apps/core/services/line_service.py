import httpx
from typing import Optional
import os
from datetime import datetime

class LineNotifyService:
    """LINE Notify Service for sending notifications"""
    
    def __init__(self):
        self.api_url = "https://notify-api.line.me/api/notify"
        self.access_token = os.getenv("LINE_NOTIFY_TOKEN")
    
    async def send_price_alert(
        self,
        symbol: str,
        stock_name: str,
        current_price: float,
        target_price: float,
        condition: str
    ) -> bool:
        """Send price alert notification"""
        
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

📊 立即查看詳情：http://localhost:5173/stock/{symbol}
        """.strip()
        
        return await self._send_message(message)
    
    async def send_news_alert(
        self,
        symbol: str,
        stock_name: str,
        news_title: str,
        sentiment: str,
        sentiment_score: float
    ) -> bool:
        """Send news alert notification"""
        
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
        
        return await self._send_message(message)
    
    async def send_transaction_notification(
        self,
        symbol: str,
        transaction_type: str,
        quantity: float,
        price: float,
        total_amount: float
    ) -> bool:
        """Send transaction notification"""
        
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
        
        return await self._send_message(message)
    
    async def _send_message(self, message: str) -> bool:
        """Send message via LINE Notify API"""
        
        if not self.access_token:
            print("LINE Notify token not configured")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {"message": message}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    data=data,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    print(f"LINE notification sent successfully")
                    return True
                else:
                    print(f"LINE notification failed: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            print(f"Error sending LINE notification: {e}")
            return False


# Global instance
line_service = LineNotifyService()