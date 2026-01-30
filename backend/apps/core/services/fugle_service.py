"""
Fugle MarketData Service
提供台股即時行情與歷史數據查詢
使用 Fugle (富果) API
"""
from fugle_marketdata import RestClient
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging

from apps.core.config import Settings

logger = logging.getLogger(__name__)
settings = Settings()


class FugleService:
    """Fugle 台股即時行情服務"""
    
    def __init__(self):
        if not settings.FUGLE_API_KEY:
            logger.warning("FUGLE_API_KEY not configured")
            self.client = None
        else:
            try:
                self.client = RestClient(api_key=settings.FUGLE_API_KEY)
                logger.info(" Fugle MarketData client initialized successfully")
            except Exception as e:
                logger.error(f" Failed to initialize Fugle client: {e}")
                self.client = None
    
    def is_available(self) -> bool:
        """檢查 Fugle API 是否可用"""
        return self.client is not None
    
    def _normalize_symbol(self, symbol: str) -> str:
        """
        標準化股票代碼（移除 .TW/.TWO 後綴）
        Fugle API 僅需要純數字代碼
        """
        if symbol.endswith('.TW') or symbol.endswith('.TWO'):
            return symbol.rsplit('.', 1)[0]
        return symbol
    
    async def get_intraday_ticker(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        取得個股即時報價
        
        Args:
            symbol: 股票代碼（如 2330 或 2330.TW）
        
        Returns:
            {
                'date': '2024-01-30',
                'symbol': '2330',
                'name': '台積電',
                'price': 625.0,
                'open': 620.0,
                'high': 630.0,
                'low': 618.0,
                'volume': 28500000,
                'change': 5.0,
                'changePercent': 0.81
            }
        """
        if not self.is_available():
            logger.warning("Fugle API not available")
            return None
        
        try:
            normalized_symbol = self._normalize_symbol(symbol)
            logger.info(f" Fetching Fugle ticker for {normalized_symbol}")
            
            stock = self.client.stock
            response = stock.intraday.ticker(symbol=normalized_symbol)
            
            if response and 'data' in response:
                data = response['data']
                result = {
                    'date': data.get('date'),
                    'symbol': data.get('symbol'),
                    'name': data.get('name'),
                    'price': data.get('closePrice') or data.get('price'),
                    'open': data.get('openPrice'),
                    'high': data.get('highPrice'),
                    'low': data.get('lowPrice'),
                    'volume': data.get('total', {}).get('tradeVolume'),
                    'change': data.get('change'),
                    'changePercent': data.get('changePercent')
                }
                logger.info(f" Fugle ticker: {result['symbol']} = ")
                return result
            
            logger.warning(f" No data in Fugle response for {normalized_symbol}")
            return None
            
        except Exception as e:
            logger.error(f" Fugle ticker error for {symbol}: {e}")
            return None
    
    async def get_intraday_candles(
        self, 
        symbol: str, 
        interval: str = '1'
    ) -> List[Dict[str, Any]]:
        """
        取得盤中 K 線數據
        
        Args:
            symbol: 股票代碼
            interval: 時間間隔（'1', '5', '15', '30', '60'）
        
        Returns:
            [
                {
                    'date': '2024-01-30 09:00:00',
                    'open': 620.0,
                    'high': 625.0,
                    'low': 618.0,
                    'close': 622.0,
                    'volume': 1000000
                },
                ...
            ]
        """
        if not self.is_available():
            return []
        
        try:
            normalized_symbol = self._normalize_symbol(symbol)
            logger.info(f" Fetching Fugle intraday candles for {normalized_symbol}")
            
            stock = self.client.stock
            response = stock.intraday.candles(symbol=normalized_symbol)
            
            if response and 'data' in response:
                candles = []
                for item in response['data']:
                    candles.append({
                        'date': item.get('date'),
                        'open': item.get('open'),
                        'high': item.get('high'),
                        'low': item.get('low'),
                        'close': item.get('close'),
                        'volume': item.get('volume')
                    })
                logger.info(f" Fugle intraday candles: {len(candles)} records")
                return candles
            
            return []
            
        except Exception as e:
            logger.error(f" Fugle intraday candles error: {e}")
            return []
    
    async def get_historical_candles(
        self, 
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        取得歷史 K 線數據
        
        Args:
            symbol: 股票代碼
            start_date: 開始日期（YYYY-MM-DD）
            end_date: 結束日期（YYYY-MM-DD）
        
        Returns:
            [
                {
                    'date': '2024-01-30',
                    'open': 620.0,
                    'high': 630.0,
                    'low': 618.0,
                    'close': 625.0,
                    'volume': 28500000
                },
                ...
            ]
        """
        if not self.is_available():
            return []
        
        try:
            normalized_symbol = self._normalize_symbol(symbol)
            
            # 預設查詢最近 90 天
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
            
            logger.info(
                f" Fetching Fugle historical candles for {normalized_symbol} "
                f"from {start_date} to {end_date}"
            )
            
            stock = self.client.stock
            response = stock.historical.candles(
                symbol=normalized_symbol,
                from_=start_date,
                to=end_date
            )
            
            if response and 'data' in response:
                candles = []
                for item in response['data']:
                    candles.append({
                        'date': item.get('date'),
                        'open': item.get('open'),
                        'high': item.get('high'),
                        'low': item.get('low'),
                        'close': item.get('close'),
                        'volume': item.get('volume')
                    })
                logger.info(f" Fugle historical candles: {len(candles)} records")
                return candles
            
            return []
            
        except Exception as e:
            logger.error(f" Fugle historical candles error: {e}")
            return []
    
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        取得完整報價（含五檔、內外盤）
        
        Returns:
            {
                'symbol': '2330',
                'price': 625.0,
                'bids': [{'price': 624.0, 'size': 100}, ...],
                'asks': [{'price': 625.0, 'size': 50}, ...],
                'total': {...}
            }
        """
        if not self.is_available():
            return None
        
        try:
            normalized_symbol = self._normalize_symbol(symbol)
            logger.info(f" Fetching Fugle quote for {normalized_symbol}")
            
            stock = self.client.stock
            response = stock.intraday.quote(symbol=normalized_symbol)
            
            if response and 'data' in response:
                logger.info(f" Fugle quote fetched for {normalized_symbol}")
                return response['data']
            
            return None
            
        except Exception as e:
            logger.error(f" Fugle quote error: {e}")
            return None


# 全域實例
fugle_service = FugleService()
