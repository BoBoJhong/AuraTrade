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
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("Gemini AI service initialized successfully")
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY not found, AI analysis disabled")
    
    def is_available(self) -> bool:
        """Check if Gemini AI service is available"""
        return self.model is not None
    
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
Analyze the following stock news and provide sentiment analysis:

Title: {title}
Summary: {summary}

Please analyze the sentiment and provide response in JSON format:
{{
    "sentiment": "positive/negative/neutral",
    "sentiment_score": -1.0 to 1.0 (negative to positive),
    "reasoning": "Brief explanation of the sentiment"
}}

Rules:
- positive: Good news for stock price (earnings beat, new products, partnerships)
- negative: Bad news for stock price (losses, scandals, lawsuits)
- neutral: Factual news without clear impact
- Score: -1.0 (very negative) to 1.0 (very positive)
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
