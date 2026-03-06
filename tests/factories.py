"""
Test Data Factory
測試數據工廠 - 生成可重用的測試數據

根據 IMPROVEMENTS.md Priority 3 實施
"""
from datetime import datetime
from typing import Dict, Any, Optional


class TestDataFactory:
    """測試數據工廠 - 統一管理測試數據生成"""
    
    @staticmethod
    def create_user_data(**overrides) -> Dict[str, Any]:
        """
        生成用戶註冊數據
        
        Args:
            **overrides: 覆蓋預設值的鍵值對
            
        Returns:
            包含用戶註冊資料的字典
            
        Example:
            data = TestDataFactory.create_user_data(email="custom@test.com")
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        
        default_data = {
            "email": f"user_{timestamp}@test.com",
            "username": f"user_{timestamp}",
            "password": "ValidPass123!",
            "confirm_password": "ValidPass123!"
        }
        
        return {**default_data, **overrides}
    
    @staticmethod
    def create_login_data(email: str, password: str) -> Dict[str, str]:
        """
        生成登入數據
        
        Args:
            email: 用戶 email
            password: 用戶密碼
            
        Returns:
            登入請求數據
        """
        return {
            "email": email,
            "password": password
        }
    
    @staticmethod
    def create_stock_data(symbol: Optional[str] = None, **overrides) -> Dict[str, Any]:
        """
        生成股票數據
        
        Args:
            symbol: 股票代碼，不提供則自動生成
            **overrides: 覆蓋預設值
            
        Returns:
            股票數據字典
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        default_data = {
            "symbol": symbol or f"TEST{timestamp[:4]}.TW",
            "name": f"測試股票_{timestamp}",
            "market": "TW",
            "price": 100.0,
            "change": 1.0,
            "changePercent": 1.0,
            "volume": 1000000
        }
        
        return {**default_data, **overrides}
    
    @staticmethod
    def create_watchlist_data(symbol: str) -> Dict[str, str]:
        """
        生成自選股數據
        
        Args:
            symbol: 股票代碼
            
        Returns:
            自選股請求數據
        """
        return {
            "symbol": symbol
        }
    
    @staticmethod
    def create_position_data(**overrides) -> Dict[str, Any]:
        """
        生成持倉數據
        
        Args:
            **overrides: 覆蓋預設值
            
        Returns:
            持倉數據字典
        """
        default_data = {
            "quantity": 100,
            "average_cost": 150.0,
            "purchase_date": datetime.utcnow().isoformat()
        }
        
        return {**default_data, **overrides}
    
    @staticmethod
    def create_alert_data(
        symbol: str,
        alert_type: str = "ABOVE",
        target_price: float = 100.0,
        **overrides
    ) -> Dict[str, Any]:
        """
        生成價格提醒數據
        
        Args:
            symbol: 股票代碼
            alert_type: 提醒類型 ('ABOVE', 'BELOW')
            target_price: 目標價格
            **overrides: 覆蓋預設值
            
        Returns:
            價格提醒數據
        """
        default_data = {
            "symbol": symbol,
            "alert_type": alert_type,
            "target_price": target_price,
            "is_active": True
        }
        
        return {**default_data, **overrides}
    
    @staticmethod
    def create_news_data(**overrides) -> Dict[str, Any]:
        """
        生成新聞數據
        
        Args:
            **overrides: 覆蓋預設值
            
        Returns:
            新聞數據字典
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        default_data = {
            "title": f"測試新聞標題_{timestamp}",
            "summary": "這是測試新聞的摘要內容",
            "source": "TestSource",
            "url": f"https://test.com/news/{timestamp}",
            "sentiment": "neutral",
            "sentiment_score": 0.0
        }
        
        return {**default_data, **overrides}


class MockDataFactory:
    """Mock 數據工廠 - 用於 Mock 外部 API 回應"""
    
    @staticmethod
    def create_yahoo_quote_response(symbol: str = "2330.TW") -> Dict[str, Any]:
        """
        生成 Yahoo Finance 報價 Mock 回應
        
        Args:
            symbol: 股票代碼
            
        Returns:
            Yahoo Finance API 格式的報價數據
        """
        return {
            "symbol": symbol,
            "shortName": "TSMC" if "2330" in symbol else "Mock Stock",
            "longName": "Taiwan Semiconductor Manufacturing Company Limited",
            "currentPrice": 500.0,
            "regularMarketPrice": 500.0,
            "regularMarketChange": 5.0,
            "regularMarketChangePercent": 1.01,
            "regularMarketVolume": 50000000,
            "marketCap": 13000000000000,
            "currency": "TWD"
        }
    
    @staticmethod
    def create_yahoo_history_response(
        symbol: str = "2330.TW",
        days: int = 30
    ) -> Dict[str, Any]:
        """
        生成 Yahoo Finance 歷史數據 Mock 回應
        
        Args:
            symbol: 股票代碼
            days: 數據天數
            
        Returns:
            歷史數據
        """
        from datetime import timedelta
        
        history = []
        base_price = 500.0
        
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days - i)
            history.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": base_price + (i % 10 - 5),
                "high": base_price + (i % 10),
                "low": base_price - (i % 10),
                "close": base_price + (i % 5 - 2),
                "volume": 50000000 + (i * 1000000)
            })
        
        return {
            "symbol": symbol,
            "history": history
        }
    
    @staticmethod
    def create_gemini_sentiment_response(
        sentiment: str = "positive",
        score: float = 0.85
    ) -> Dict[str, Any]:
        """
        生成 Gemini AI 情緒分析 Mock 回應
        
        Args:
            sentiment: 情緒 ('positive', 'negative', 'neutral')
            score: 情緒分數 (-1.0 to 1.0)
            
        Returns:
            Gemini AI 格式的情緒分析結果
        """
        return {
            "sentiment": sentiment,
            "score": score,
            "confidence": 0.92,
            "summary": "AI 分析摘要"
        }
    
    @staticmethod
    def create_technical_indicators_response(symbol: str = "2330.TW") -> Dict[str, Any]:
        """
        生成技術指標 Mock 回應
        
        Args:
            symbol: 股票代碼
            
        Returns:
            技術指標數據
        """
        return {
            "symbol": symbol,
            "ma5": 498.5,
            "ma10": 495.2,
            "ma20": 490.8,
            "ma60": 485.3,
            "macd": {
                "macd": 2.5,
                "signal": 1.8,
                "histogram": 0.7
            },
            "rsi": 65.5,
            "kdj": {
                "k": 75.2,
                "d": 72.8,
                "j": 80.0
            }
        }
