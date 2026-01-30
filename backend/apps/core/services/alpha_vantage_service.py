"""
Alpha Vantage Service
提供美股即時行情、歷史數據、技術指標與新聞情緒分析
使用 Alpha Vantage API
官方文檔: https://www.alphavantage.co/documentation/
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging

from apps.core.config import Settings

logger = logging.getLogger(__name__)
settings = Settings()


class AlphaVantageService:
    """Alpha Vantage 美股數據服務"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self):
        self.api_key = settings.ALPHA_VANTAGE_API_KEY
        if not self.api_key:
            logger.warning("ALPHA_VANTAGE_API_KEY not configured")
    
    def is_available(self) -> bool:
        """檢查 Alpha Vantage API 是否可用"""
        return bool(self.api_key)
    
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        取得即時報價（GLOBAL_QUOTE）
        
        Args:
            symbol: 股票代碼（如 AAPL, MSFT）
        
        Returns:
            {
                'symbol': 'AAPL',
                'price': 185.5,
                'open': 183.2,
                'high': 186.0,
                'low': 182.8,
                'volume': 45000000,
                'change': 2.3,
                'changePercent': 1.26
            }
        """
        if not self.is_available():
            logger.warning("Alpha Vantage API not available")
            return None
        
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            logger.info(f" Fetching Alpha Vantage quote for {symbol}")
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'Global Quote' in data and data['Global Quote']:
                quote = data['Global Quote']
                result = {
                    'symbol': quote.get('01. symbol'),
                    'price': float(quote.get('05. price', 0)),
                    'open': float(quote.get('02. open', 0)),
                    'high': float(quote.get('03. high', 0)),
                    'low': float(quote.get('04. low', 0)),
                    'volume': int(quote.get('06. volume', 0)),
                    'change': float(quote.get('09. change', 0)),
                    'changePercent': float(quote.get('10. change percent', '0').replace('%', ''))
                }
                logger.info(f"✅ Alpha Vantage quote: {result['symbol']} = ${result['price']}")
                return result
            
            # 檢查是否超過 API 限制
            if 'Note' in data:
                logger.warning(f" Alpha Vantage rate limit: {data['Note']}")
            elif 'Error Message' in data:
                logger.error(f" Alpha Vantage error: {data['Error Message']}")
            
            return None
            
        except Exception as e:
            logger.error(f" Alpha Vantage quote error for {symbol}: {e}")
            return None
    
    async def get_daily_data(
        self, 
        symbol: str,
        outputsize: str = 'compact'
    ) -> List[Dict[str, Any]]:
        """
        取得每日歷史數據（TIME_SERIES_DAILY）
        
        Args:
            symbol: 股票代碼
            outputsize: 'compact' (最近 100 天) 或 'full' (20+ 年)
        
        Returns:
            [
                {
                    'date': '2024-01-30',
                    'open': 183.2,
                    'high': 186.0,
                    'low': 182.8,
                    'close': 185.5,
                    'volume': 45000000
                },
                ...
            ]
        """
        if not self.is_available():
            return []
        
        try:
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'outputsize': outputsize,
                'apikey': self.api_key
            }
            
            logger.info(f" Fetching Alpha Vantage daily data for {symbol}")
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'Time Series (Daily)' in data:
                time_series = data['Time Series (Daily)']
                result = []
                for date_str, values in sorted(time_series.items()):
                    result.append({
                        'date': date_str + 'T00:00:00',
                        'open': float(values.get('1. open', 0)),
                        'high': float(values.get('2. high', 0)),
                        'low': float(values.get('3. low', 0)),
                        'close': float(values.get('4. close', 0)),
                        'volume': int(values.get('5. volume', 0))
                    })
                logger.info(f" Alpha Vantage daily data: {len(result)} records")
                return result
            
            # 檢查錯誤訊息
            if 'Note' in data:
                logger.warning(f" Alpha Vantage rate limit: {data['Note']}")
            elif 'Error Message' in data:
                logger.error(f" Alpha Vantage error: {data['Error Message']}")
            
            return []
            
        except Exception as e:
            logger.error(f" Alpha Vantage daily data error: {e}")
            return []
    
    async def get_technical_indicator(
        self,
        symbol: str,
        indicator: str,
        interval: str = 'daily',
        time_period: int = 14,
        series_type: str = 'close'
    ) -> Optional[Dict[str, Any]]:
        """
        取得技術指標（60+ 種技術指標）
        
        Args:
            symbol: 股票代碼
            indicator: 指標名稱（SMA, EMA, MACD, RSI, BBANDS, etc.）
            interval: 時間間隔（daily, weekly, monthly）
            time_period: 計算期間（如 RSI 14天）
            series_type: 價格類型（close, open, high, low）
        
        Returns:
            {
                'indicator': 'RSI',
                'data': [
                    {'date': '2024-01-30', 'value': 65.5},
                    ...
                ]
            }
        """
        if not self.is_available():
            return None
        
        try:
            params = {
                'function': indicator.upper(),
                'symbol': symbol,
                'interval': interval,
                'time_period': time_period,
                'series_type': series_type,
                'apikey': self.api_key
            }
            
            logger.info(f" Fetching Alpha Vantage {indicator} for {symbol}")
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Alpha Vantage 技術指標回應格式為 "Technical Analysis: {indicator}"
            key = f"Technical Analysis: {indicator.upper()}"
            if key in data:
                indicator_data = data[key]
                result = {
                    'indicator': indicator.upper(),
                    'data': []
                }
                for date_str, values in sorted(indicator_data.items()):
                    # 不同指標有不同的值欄位
                    if indicator.upper() == 'MACD':
                        result['data'].append({
                            'date': date_str,
                            'MACD': float(values.get('MACD', 0)),
                            'MACD_Signal': float(values.get('MACD_Signal', 0)),
                            'MACD_Hist': float(values.get('MACD_Hist', 0))
                        })
                    else:
                        # 大多數指標只有一個值
                        value_key = list(values.keys())[0] if values else None
                        if value_key:
                            result['data'].append({
                                'date': date_str,
                                'value': float(values[value_key])
                            })
                
                logger.info(f" Alpha Vantage {indicator}: {len(result['data'])} records")
                return result
            
            return None
            
        except Exception as e:
            logger.error(f" Alpha Vantage indicator error: {e}")
            return None
    
    async def get_news_sentiment(
        self,
        tickers: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        取得新聞情緒分析（NEWS_SENTIMENT）
        
        Args:
            tickers: 股票代碼（逗號分隔，如 'AAPL,MSFT'）
            limit: 新聞數量限制
        
        Returns:
            [
                {
                    'title': 'Apple releases new iPhone',
                    'summary': '...',
                    'url': 'https://...',
                    'time_published': '20240130T120000',
                    'overall_sentiment_score': 0.35,
                    'overall_sentiment_label': 'Bullish'
                },
                ...
            ]
        """
        if not self.is_available():
            return []
        
        try:
            params = {
                'function': 'NEWS_SENTIMENT',
                'apikey': self.api_key,
                'limit': limit
            }
            if tickers:
                params['tickers'] = tickers
            
            logger.info(f" Fetching Alpha Vantage news sentiment for {tickers or 'general'}")
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'feed' in data:
                news_list = []
                for article in data['feed'][:limit]:
                    news_list.append({
                        'title': article.get('title'),
                        'summary': article.get('summary'),
                        'url': article.get('url'),
                        'time_published': article.get('time_published'),
                        'overall_sentiment_score': float(article.get('overall_sentiment_score', 0)),
                        'overall_sentiment_label': article.get('overall_sentiment_label'),
                        'source': article.get('source')
                    })
                logger.info(f" Alpha Vantage news: {len(news_list)} articles")
                return news_list
            
            return []
            
        except Exception as e:
            logger.error(f" Alpha Vantage news error: {e}")
            return []


# 全域實例
alpha_vantage_service = AlphaVantageService()
ALPHA_VANTAGE_AVAILABLE = alpha_vantage_service.is_available()
