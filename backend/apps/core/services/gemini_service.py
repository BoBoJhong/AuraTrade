import google.generativeai as genai
import os
import logging
from typing import Dict, Optional
import json

logger = logging.getLogger(__name__)

class GeminiService:
    """Google Gemini AI Service for stock news sentiment analysis"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # Use available model: gemini-flash-latest or gemini-pro-latest
            self.model = genai.GenerativeModel('models/gemini-flash-latest')
            logger.info("Gemini AI service initialized successfully with gemini-flash-latest")
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY not found, AI analysis disabled")
    
    def is_available(self) -> bool:
        """Check if Gemini AI service is available"""
        return self.model is not None
    
    async def generate_text(self, prompt: str) -> Optional[str]:
        """
        Generate text response from Gemini AI
        
        Args:
            prompt: Text prompt for generation
        
        Returns:
            Generated text or None if failed
        """
        if not self.is_available():
            return None
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini text generation failed: {e}")
            return None
    
    async def analyze_news_sentiment(
        self,
        title: str,
        summary: str
    ) -> Dict[str, any]:
        """
        Analyze news sentiment using Gemini AI
        
        Args:
            title: News title
            summary: News summary
        
        Returns:
            Dict with sentiment, sentiment_score, and reasoning
        """
        if not self.is_available():
            return {
                "sentiment": "neutral",
                "sentiment_score": 0.0,
                "reasoning": "AI service not available"
            }
        
        try:
            prompt = f"""
你是專業的股市分析師。分析以下股票新聞的情緒傾向：

標題: {title}
摘要: {summary}

請以 JSON 格式回答：
{{
    "sentiment": "positive/negative/neutral",
    "sentiment_score": -1.0 到 1.0 之間的數字,
    "reasoning": "簡短說明判斷依據"
}}

判斷標準（要敏銳識別情緒）：
【利多 positive】分數 +0.3 到 +1.0：
- 股價上漲、突破新高、創新高
- 營收/獲利成長、超出預期
- 獲獎、排名提升、市占率增加
- 新產品、新訂單、新合作
- 分析師看好、目標價上調
- 大單買進、外資買超

【利空 negative】分數 -0.3 到 -1.0：
- 股價下跌、跌破支撐、翻黑
- 營收/獲利衰退、不如預期
- 賣壓、大量賣出、外資賣超
- 裁員、虧損、訴訟、醜聞
- 分析師降評、目標價下調

【中性 neutral】分數 -0.2 到 +0.2：
- 純粹數據陳述，無明顯正負面意涵
- 例如：「收盤價XXX元」「成交量XXX張」

注意：只有完全中立的事實陳述才判定為 neutral，有任何正負面傾向都要明確標示！
"""
            
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Try to parse JSON from response
            if "```json" in result_text:
                json_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                json_text = result_text.split("```")[1].split("```")[0].strip()
            else:
                json_text = result_text
            
            result = json.loads(json_text)
            
            # Validate result
            sentiment = result.get("sentiment", "neutral")
            if sentiment not in ["positive", "negative", "neutral"]:
                sentiment = "neutral"
            
            sentiment_score = float(result.get("sentiment_score", 0.0))
            sentiment_score = max(-1.0, min(1.0, sentiment_score))
            
            return {
                "sentiment": sentiment,
                "sentiment_score": sentiment_score,
                "reasoning": result.get("reasoning", "")
            }
            
        except Exception as e:
            logger.error(f"Gemini sentiment analysis failed: {e}")
            return {
                "sentiment": "neutral",
                "sentiment_score": 0.0,
                "reasoning": f"Analysis failed: {str(e)}"
            }
    
    async def generate_investment_advice(
        self,
        symbol: str,
        current_price: float,
        indicators: Dict,
        sentiment: str
    ) -> Dict[str, any]:
        """
        Generate investment advice based on technical indicators and news sentiment
        
        Args:
            symbol: Stock symbol
            current_price: Current stock price
            indicators: Technical indicators (RSI, MACD, etc.)
            sentiment: News sentiment (positive/negative/neutral)
        
        Returns:
            Dict with action, reasoning, confidence, and risk_level
        """
        if not self.is_available():
            return {
                "action": "hold",
                "reasoning": "AI service not available",
                "confidence": 0.0,
                "risk_level": "unknown"
            }
        
        try:
            prompt = f"""
As a professional stock analyst, provide investment advice for {symbol}:

Current Price: ${current_price}
Technical Indicators: {json.dumps(indicators, indent=2)}
News Sentiment: {sentiment}

Provide your advice in JSON format:
{{
    "action": "buy/sell/hold",
    "reasoning": "Detailed reasoning for the recommendation",
    "confidence": 0.0 to 1.0 (how confident are you),
    "risk_level": "low/medium/high"
}}

Consider:
1. Technical indicators (RSI, MACD, moving averages)
2. News sentiment impact
3. Overall market conditions
4. Risk factors
"""
            
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Parse JSON
            if "```json" in result_text:
                json_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                json_text = result_text.split("```")[1].split("```")[0].strip()
            else:
                json_text = result_text
            
            result = json.loads(json_text)
            
            # Validate result
            action = result.get("action", "hold")
            if action not in ["buy", "sell", "hold"]:
                action = "hold"
            
            confidence = float(result.get("confidence", 0.5))
            confidence = max(0.0, min(1.0, confidence))
            
            risk_level = result.get("risk_level", "medium")
            if risk_level not in ["low", "medium", "high"]:
                risk_level = "medium"
            
            return {
                "action": action,
                "reasoning": result.get("reasoning", ""),
                "confidence": confidence,
                "risk_level": risk_level
            }
            
        except Exception as e:
            logger.error(f"Gemini investment advice failed: {e}")
            return {
                "action": "hold",
                "reasoning": f"Analysis failed: {str(e)}",
                "confidence": 0.0,
                "risk_level": "high"
            }

# Global instance
gemini_service = GeminiService()
