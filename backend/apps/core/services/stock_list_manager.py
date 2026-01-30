"""
股票清單管理器 - 提供完整的台股 + 美股代號查詢
支援多數據源：台灣證交所、櫃買中心、Yahoo Finance
"""
import requests
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import redis.asyncio as redis
from apps.core.config import settings

logger = logging.getLogger(__name__)


class StockListManager:
    """管理完整的股票清單，支援台股 + 美股"""
    
    CACHE_KEY = "stock_list:all"
    CACHE_EXPIRY = 86400  # 24 小時更新一次
    
    # 台灣證交所 API
    TWSE_LISTED_API = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
    TPEX_OTC_API = "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_daily_close_quotes"
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.stock_list = []
    
    async def get_all_stocks(self, force_refresh: bool = False) -> List[Dict]:
        """獲取所有股票清單（優先從快取）"""
        if not force_refresh:
            cached = await self._get_from_cache()
            if cached:
                logger.info(f"從快取載入 {len(cached)} 檔股票")
                return cached
        
        logger.info("開始更新股票清單...")
        stocks = await self._fetch_all_stocks()
        await self._save_to_cache(stocks)
        logger.info(f"✅ 已更新 {len(stocks)} 檔股票")
        return stocks
    
    async def _fetch_all_stocks(self) -> List[Dict]:
        """從多個來源抓取股票清單"""
        all_stocks = []
        seen_symbols = set()  # 去重
        
        # 1. 台灣上市股票（TWSE）- 包含股票 + ETF
        twse_stocks = await self._fetch_twse_stocks()
        for stock in twse_stocks:
            if stock['symbol'] not in seen_symbols:
                all_stocks.append(stock)
                seen_symbols.add(stock['symbol'])
        logger.info(f"✅ 台灣上市: {len(twse_stocks)} 檔")
        
        # 2. 台灣上櫃股票（TPEX）
        tpex_stocks = await self._fetch_tpex_stocks()
        for stock in tpex_stocks:
            if stock['symbol'] not in seen_symbols:
                all_stocks.append(stock)
                seen_symbols.add(stock['symbol'])
        logger.info(f"✅ 台灣上櫃: {len(tpex_stocks)} 檔")
        
        # 3. 熱門 ETF 補充（如果 API 沒抓到）
        etf_list = self._get_popular_etfs()
        for stock in etf_list:
            if stock['symbol'] not in seen_symbols:
                all_stocks.append(stock)
                seen_symbols.add(stock['symbol'])
        logger.info(f"✅ 熱門 ETF 補充: {len([s for s in etf_list if s['symbol'] in seen_symbols])} 檔已存在")
        
        # 4. 常見美股
        us_stocks = self._get_popular_us_stocks()
        all_stocks.extend(us_stocks)
        logger.info(f"✅ 美股: {len(us_stocks)} 檔")
        
        return all_stocks
    
    async def _fetch_twse_stocks(self) -> List[Dict]:
        """抓取台灣上市股票"""
        try:
            response = requests.get(self.TWSE_LISTED_API, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            stocks = []
            for item in data:
                code = item.get('Code', '').strip()
                name = item.get('Name', '').strip()
                
                # 不過濾長度，包含 ETF（如 006208）
                if not code or not name:
                    continue
                
                stocks.append({
                    'symbol': f"{code}.TW",
                    'name': name,
                    'market': 'TWSE',
                    'type': 'ETF' if code.startswith('00') else 'stock'
                })
            
            return stocks
        except Exception as e:
            logger.error(f"抓取台灣上市股票失敗: {e}")
            return []
    
    async def _fetch_tpex_stocks(self) -> List[Dict]:
        """抓取台灣上櫃股票"""
        try:
            response = requests.get(self.TPEX_OTC_API, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            stocks = []
            for item in data:
                code = item.get('SecuritiesCompanyCode', '').strip()
                name = item.get('CompanyName', '').strip()
                
                if not code or not name:
                    continue
                
                stocks.append({
                    'symbol': f"{code}.TWO",
                    'name': name,
                    'market': 'TPEX',
                    'type': 'stock'
                })
            
            return stocks
        except Exception as e:
            logger.error(f"抓取台灣上櫃股票失敗: {e}")
            return []
    
    def _get_popular_etfs(self) -> List[Dict]:
        """熱門 ETF 清單（確保重要 ETF 不會被遺漏）"""
        return [
            {'symbol': '0050.TW', 'name': '元大台灣50', 'market': 'TWSE', 'type': 'ETF'},
            {'symbol': '0056.TW', 'name': '元大高股息', 'market': 'TWSE', 'type': 'ETF'},
            {'symbol': '006208.TW', 'name': '富邦台50', 'market': 'TWSE', 'type': 'ETF'},
            {'symbol': '00878.TW', 'name': '國泰永續高股息', 'market': 'TWSE', 'type': 'ETF'},
            {'symbol': '00679B.TW', 'name': '元大美債20年', 'market': 'TWSE', 'type': 'ETF'},
            {'symbol': '00881.TW', 'name': '國泰台灣5G+', 'market': 'TWSE', 'type': 'ETF'},
            {'symbol': '00882.TW', 'name': '中信中國高股息', 'market': 'TWSE', 'type': 'ETF'},
        ]
    
    def _get_popular_us_stocks(self) -> List[Dict]:
        """常見美股清單"""
        return [
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'market': 'US', 'type': 'stock'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'market': 'US', 'type': 'stock'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'market': 'US', 'type': 'stock'},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'market': 'US', 'type': 'stock'},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'market': 'US', 'type': 'stock'},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'market': 'US', 'type': 'stock'},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'market': 'US', 'type': 'stock'},
            {'symbol': 'BRK-B', 'name': 'Berkshire Hathaway', 'market': 'US', 'type': 'stock'},
            {'symbol': 'JPM', 'name': 'JPMorgan Chase', 'market': 'US', 'type': 'stock'},
            {'symbol': 'V', 'name': 'Visa Inc.', 'market': 'US', 'type': 'stock'},
        ]
    
    async def search_stocks(self, query: str, limit: int = 20) -> List[Dict]:
        """搜尋股票（支援代號、名稱模糊搜尋）"""
        all_stocks = await self.get_all_stocks()
        query = query.upper().strip()
        
        # 去除 .TW / .TWO 後綴
        query_without_suffix = query.replace('.TW', '').replace('.TWO', '')
        
        results = []
        for stock in all_stocks:
            symbol = stock['symbol'].upper()
            name = stock['name']
            
            # 完全匹配優先
            if query == symbol or query_without_suffix == symbol.split('.')[0]:
                results.insert(0, stock)
                continue
            
            # 模糊匹配
            if (query in symbol or 
                query_without_suffix in symbol or 
                query in name or 
                query_without_suffix in name):
                results.append(stock)
            
            if len(results) >= limit:
                break
        
        return results[:limit]
    
    async def _get_from_cache(self) -> Optional[List[Dict]]:
        """從 Redis 快取讀取"""
        try:
            cached = await self.redis_client.get(self.CACHE_KEY)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.error(f"讀取快取失敗: {e}")
        return None
    
    async def _save_to_cache(self, stocks: List[Dict]):
        """儲存到 Redis 快取"""
        try:
            await self.redis_client.setex(
                self.CACHE_KEY,
                self.CACHE_EXPIRY,
                json.dumps(stocks, ensure_ascii=False)
            )
        except Exception as e:
            logger.error(f"儲存快取失敗: {e}")


# 全域實例
stock_list_manager = StockListManager()
