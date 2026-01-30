import yfinance as yf
import pandas as pd
import requests
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, date
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import random

logger = logging.getLogger(__name__)

import json
import redis.asyncio as redis
from apps.core.config import settings
from apps.core.services.stock_list_manager import stock_list_manager

# Import new data sources
try:
    from apps.core.services.twse_service import TWSEService
    from apps.core.services.finmind_service import FinMindService
    TAIWAN_SOURCES_AVAILABLE = True
except ImportError:
    TAIWAN_SOURCES_AVAILABLE = False
    logger.warning("TWSE and FinMind services not available")

# Import Fugle service for Taiwan stock real-time data
try:
    from apps.core.services.fugle_service import fugle_service
    FUGLE_AVAILABLE = fugle_service.is_available()
    if FUGLE_AVAILABLE:
        logger.info("✅ Fugle MarketData service available")
except ImportError:
    FUGLE_AVAILABLE = False
    logger.warning("Fugle MarketData service not available")

# Import Alpha Vantage service for US stocks and technical indicators
try:
    from apps.core.services.alpha_vantage_service import alpha_vantage_service
    ALPHA_VANTAGE_AVAILABLE = alpha_vantage_service.is_available()
    if ALPHA_VANTAGE_AVAILABLE:
        logger.info("✅ Alpha Vantage service available")
except ImportError:
    ALPHA_VANTAGE_AVAILABLE = False
    logger.warning("Alpha Vantage service not available")

# Initialize Redis client
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

# Mock data for testing when Yahoo Finance is rate limited
# 更新日期: 2026-01-30 (使用最新市場價格)
MOCK_STOCKS = {
    # 台股權值股
    "2330.TW": {"name": "台積電", "price": 1775.0, "market": "TW", "sector": "半導體"},
    "2317.TW": {"name": "鴻海", "price": 215.5, "market": "TW", "sector": "電子製造"},
    "2311.TW": {"name": "日月光投控", "price": 145.5, "market": "TW", "sector": "半導體"},
    "2454.TW": {"name": "聯發科", "price": 1185.0, "market": "TW", "sector": "半導體"},
    "2308.TW": {"name": "台達電", "price": 398.5, "market": "TW", "sector": "電子"},
    "2882.TW": {"name": "國泰金", "price": 68.2, "market": "TW", "sector": "金融"},
    "2412.TW": {"name": "中華電", "price": 128.5, "market": "TW", "sector": "電信"},
    "2881.TW": {"name": "富邦金", "price": 89.7, "market": "TW", "sector": "金融"},
    # ETF
    "0050.TW": {"name": "元大台灣50", "price": 182.5, "market": "TW", "sector": "ETF"},
    "006208.TW": {"name": "富邦台50", "price": 90.2, "market": "TW", "sector": "ETF"},
    "0056.TW": {"name": "元大高股息", "price": 39.8, "market": "TW", "sector": "ETF"},
    "00878.TW": {"name": "國泰永續高股息", "price": 25.1, "market": "TW", "sector": "ETF"},
    "00679B.TW": {"name": "元大美債20年", "price": 35.6, "market": "TW", "sector": "ETF"},
    # 美股
    "AAPL": {"name": "Apple Inc.", "price": 151.5, "market": "US", "sector": "Technology"},
    "TSLA": {"name": "Tesla Inc.", "price": 262.0, "market": "US", "sector": "Automotive"},
    "MSFT": {"name": "Microsoft Corporation", "price": 405.2, "market": "US", "sector": "Technology"},
    "GOOGL": {"name": "Alphabet Inc.", "price": 142.8, "market": "US", "sector": "Technology"},
    "NVDA": {"name": "NVIDIA Corporation", "price": 505.3, "market": "US", "sector": "Technology"},
    "AMZN": {"name": "Amazon.com Inc.", "price": 178.9, "market": "US", "sector": "E-commerce"},
    "META": {"name": "Meta Platforms Inc.", "price": 482.6, "market": "US", "sector": "Technology"},
}

class YahooFinanceService:
    """
    Service to interact with Yahoo Finance API via yfinance library
    Handles data fetching with Redis caching
    多層備援策略: yfinance API -> Web Scraper -> Mock Data
    """
    
    @staticmethod
    def _scrape_historical_data(symbol: str, period: str = '1mo') -> Optional[List[Dict[str, Any]]]:
        """
        從 Yahoo Finance 網頁爬取歷史數據 (備援方案)
        當 yfinance API 失敗時使用
        """
        try:
            # 計算時間範圍
            end_date = datetime.now()
            if period == '1d':
                start_date = end_date - timedelta(days=2)
            elif period == '5d':
                start_date = end_date - timedelta(days=7)
            elif period == '1mo':
                start_date = end_date - timedelta(days=35)
            elif period == '3mo':
                start_date = end_date - timedelta(days=100)
            elif period == '1y':
                start_date = end_date - timedelta(days=380)
            else:
                start_date = end_date - timedelta(days=35)
            
            # Unix timestamp
            period1 = int(start_date.timestamp())
            period2 = int(end_date.timestamp())
            
            # Yahoo Finance CSV 下載端點
            url = f'https://query1.finance.yahoo.com/v7/finance/download/{symbol}'
            params = {
                'period1': period1,
                'period2': period2,
                'interval': '1d',
                'events': 'history',
                'includeAdjustedClose': 'true'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 解析 CSV
            lines = response.text.strip().split('\n')
            if len(lines) < 2:
                return None
            
            data = []
            for line in lines[1:]:  # 跳過 header
                values = line.split(',')
                if len(values) >= 6:
                    try:
                        # CSV format: Date,Open,High,Low,Close,Adj Close,Volume
                        data.append({
                            'date': values[0] + 'T00:00:00',  # Add time component
                            'open': float(values[1]),
                            'high': float(values[2]),
                            'low': float(values[3]),
                            'close': float(values[4]),
                            'volume': int(float(values[6])) if len(values) > 6 and values[6] != 'null' else 0
                        })
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Failed to parse line: {line}, error: {e}")
                        continue
            
            if data:
                logger.info(f'✅ Scraped {len(data)} records for {symbol} from Yahoo Finance CSV API')
                return data
            return None
            
        except Exception as e:
            logger.error(f'❌ Scraper failed for {symbol}: {str(e)}')
            return None
    
    @staticmethod
    def _get_mock_data(symbol: str) -> Optional[Dict[str, Any]]:
        """Get mock data when Yahoo Finance API is unavailable"""
        # Try exact match first
        if symbol in MOCK_STOCKS:
            mock = MOCK_STOCKS[symbol]
            return {
                "symbol": symbol,
                "name": mock["name"],
                "market": mock["market"],
                "sector": mock.get("sector"),
                "industry": None,
                "currency": "TWD" if mock["market"] == "TW" else "USD",
                "price": mock["price"],
                "change": round(random.uniform(-5, 5), 2),
                "change_percent": round(random.uniform(-2, 2), 2),
                "volume": random.randint(10000000, 50000000),
                "market_cap": random.randint(1000000000, 5000000000),
                "pe_ratio": round(random.uniform(15, 35), 2),
                "updated_at": datetime.utcnow().isoformat()
            }
        
        # Try with .TW suffix for Taiwan stocks
        if symbol.isdigit():
            tw_symbol = f"{symbol}.TW"
            if tw_symbol in MOCK_STOCKS:
                return YahooFinanceService._get_mock_data(tw_symbol)
        
        return None

    @staticmethod
    async def get_stock_info(symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a stock with caching (TTL: 1 hour)
        Falls back to mock data if Yahoo Finance API is rate limited
        """
        cache_key = f"stock:info:{symbol}"
        
        # Try cache
        try:
            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Redis get error: {e}")

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # yfinance info can be empty or have "regularMarketPrice" missing if symbol is invalid
            if not info or 'symbol' not in info:
                # Double check with history
                hist = ticker.history(period="1d")
                if hist.empty:
                    # Try mock data before returning None
                    logger.info(f"No data from Yahoo Finance for {symbol}, trying mock data")
                    return YahooFinanceService._get_mock_data(symbol)
            
            result = {
                "symbol": info.get("symbol", symbol),
                "name": info.get("longName", info.get("shortName", symbol)),
                "market": "TW" if ".TW" in symbol or ".TWO" in symbol else "US",
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "currency": info.get("currency"),
                "price": info.get("currentPrice", info.get("regularMarketPrice")),
                "change": info.get("regularMarketChange"),
                "change_percent": info.get("regularMarketChangePercent"),
                "volume": info.get("regularMarketVolume"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "updated_at": datetime.utcnow().isoformat() # ISO format for JSON serialization
            }
            
            # Save to cache
            try:
                await redis_client.setex(cache_key, 3600, json.dumps(result))
            except Exception as e:
                logger.warning(f"Redis set error: {e}")
                
            return result
        except Exception as e:
            logger.error(f"Error fetching info for {symbol}: {str(e)}")
            # Try mock data as fallback
            logger.info(f"Fallback to mock data for {symbol}")
            return YahooFinanceService._get_mock_data(symbol)

    @staticmethod
    async def get_stock_price(symbol: str) -> Optional[float]:
        """
        Get real-time (or delayed) price for a stock (TTL: 60 seconds)
        
        策略優化（整合 Fugle）:
        - 台股盤中: Fugle → Yahoo Finance → TWSE → FinMind → Mock
        - 台股盤後: TWSE → FinMind → Fugle → Yahoo Finance → Mock
        - 美股: Yahoo Finance → Mock
        
        原因: 
        - Fugle 提供台股即時報價，優於其他來源
        - TWSE/FinMind 盤後提供精確收盤價
        - Yahoo Finance 作為全球備援
        """
        cache_key = f"stock:price:{symbol}"
        
        # Layer 1: Try Redis cache (60s)
        try:
            cached = await redis_client.get(cache_key)
            if cached:
                logger.info(f"✅ 股價來源: Redis Cache - {symbol}")
                return float(cached)
        except Exception as e:
            logger.warning(f"Redis get error: {e}")

        price = None
        is_taiwan_stock = ".TW" in symbol or ".TWO" in symbol
        
        # 判斷是否為台股交易時間 (09:00-13:30 UTC+8)
        now = datetime.now()
        is_trading_hours = (9 <= now.hour < 13) or (now.hour == 13 and now.minute <= 30)
        
        # 台股交易時間: 優先使用 Fugle (即時報價)
        if is_taiwan_stock and is_trading_hours:
            # Layer 2a: Fugle API (台股即時報價 - 最優先)
            if FUGLE_AVAILABLE and price is None:
                try:
                    ticker_data = await fugle_service.get_intraday_ticker(symbol)
                    if ticker_data and ticker_data.get('price'):
                        price = float(ticker_data['price'])
                        logger.info(f"✅ 股價來源: Fugle 即時 (盤中) - {symbol} = ${price}")
                except Exception as e:
                    logger.warning(f"Fugle API failed for {symbol}: {e}")
            
            # Layer 2b: Yahoo Finance API (盤中即時報價 - 備援)
            if price is None:
                try:
                    ticker = yf.Ticker(symbol)
                    # 使用 ticker.info 獲取最新價格，比 history 更可靠
                    info = ticker.info
                    if info and (info.get('currentPrice') or info.get('regularMarketPrice')):
                        price = float(info.get('currentPrice') or info.get('regularMarketPrice'))
                        logger.info(f"✅ 股價來源: Yahoo Finance info (盤中) - {symbol} = ${price}")
                    elif info and info.get('previousClose'):
                        # 如果沒有當前價格，使用前收盤價
                        price = float(info.get('previousClose'))
                        logger.info(f"✅ 股價來源: Yahoo Finance previousClose (盤中) - {symbol} = ${price}")
                    else:
                        # Fallback to history
                        df = ticker.history(period="1d")
                        if not df.empty:
                            price = float(df['Close'].iloc[-1])
                            logger.info(f"✅ 股價來源: Yahoo Finance history (盤中) - {symbol} = ${price}")
                except Exception as e:
                    logger.warning(f"Yahoo Finance failed for {symbol}: {e}")
            
            # Layer 2c: TWSE fallback (盤中可能是前收)
            if price is None and TAIWAN_SOURCES_AVAILABLE:
                try:
                    info = TWSEService.get_stock_info(symbol)
                    if info and info.get('price'):
                        price = float(info['price'])
                        logger.info(f"✅ 股價來源: TWSE (盤中fallback) - {symbol} = ${price}")
                except Exception as e:
                    logger.warning(f"TWSE API failed: {e}")
        
        # 台股盤後: 優先使用 TWSE/FinMind (精確收盤價)
        elif is_taiwan_stock and TAIWAN_SOURCES_AVAILABLE:
            # Layer 2a: TWSE Official API (盤後收盤價)
            try:
                info = TWSEService.get_stock_info(symbol)
                if info and info.get('price'):
                    price = float(info['price'])
                    logger.info(f"✅ 股價來源: TWSE 官方 (盤後) - {symbol} = ${price}")
            except Exception as e:
                logger.warning(f"TWSE API failed: {e}")
            
            # Layer 2b: FinMind fallback
            if price is None:
                try:
                    info = FinMindService.get_stock_info(symbol)
                    if info and info.get('price'):
                        price = float(info['price'])
                        logger.info(f"✅ 股價來源: FinMind (盤後) - {symbol} = ${price}")
                except Exception as e:
                    logger.warning(f"FinMind API failed: {e}")
            
            # Layer 2c: Yahoo Finance fallback
            if price is None:
                try:
                    ticker = yf.Ticker(symbol)
                    # 優先使用 info 獲取價格
                    info = ticker.info
                    if info and (info.get('currentPrice') or info.get('regularMarketPrice')):
                        price = float(info.get('currentPrice') or info.get('regularMarketPrice'))
                        logger.info(f"✅ 股價來源: Yahoo Finance info (盤後) - {symbol} = ${price}")
                    elif info and info.get('previousClose'):
                        price = float(info.get('previousClose'))
                        logger.info(f"✅ 股價來源: Yahoo Finance previousClose (盤後) - {symbol} = ${price}")
                    else:
                        # Fallback to history
                        df = ticker.history(period="1d")
                        if not df.empty:
                            price = float(df['Close'].iloc[-1])
                            logger.info(f"✅ 股價來源: Yahoo Finance history (盤後) - {symbol} = ${price}")
                except Exception as e:
                    logger.warning(f"Yahoo Finance failed: {e}")
        
        # 美股: 優先使用 Alpha Vantage，備援 Yahoo Finance
        else:
            # Layer 2a: Alpha Vantage API (美股即時報價 - 最優先)
            if ALPHA_VANTAGE_AVAILABLE and price is None:
                try:
                    quote_data = await alpha_vantage_service.get_quote(symbol)
                    if quote_data and quote_data.get('price'):
                        price = float(quote_data['price'])
                        logger.info(f"✅ 股價來源: Alpha Vantage (美股) - {symbol} = ${price}")
                except Exception as e:
                    logger.warning(f"Alpha Vantage failed for {symbol}: {e}")
            
            # Layer 2b: Yahoo Finance (美股備援)
            if price is None:
                try:
                    ticker = yf.Ticker(symbol)
                    # 優先使用 info 獲取最新價格
                    info = ticker.info
                    if info and (info.get('currentPrice') or info.get('regularMarketPrice')):
                        price = float(info.get('currentPrice') or info.get('regularMarketPrice'))
                        logger.info(f"✅ 股價來源: Yahoo Finance info - {symbol} = ${price}")
                    elif info and info.get('previousClose'):
                        price = float(info.get('previousClose'))
                        logger.info(f"✅ 股價來源: Yahoo Finance previousClose - {symbol} = ${price}")
                    else:
                        # Fallback to history
                        df = ticker.history(period="1d")
                        if not df.empty:
                            price = float(df['Close'].iloc[-1])
                            logger.info(f"✅ 股價來源: Yahoo Finance history - {symbol} = ${price}")
                except Exception as e:
                    logger.warning(f"Yahoo Finance failed for {symbol}: {e}")
        
        # Final fallback: Mock data (development)
        if price is None and symbol in MOCK_STOCKS:
            price = MOCK_STOCKS[symbol]['price']
            logger.info(f"⚠️ 股價來源: Mock Data - {symbol} = ${price}")
        
        # Save to cache if we got a valid price
        if price is not None:
            try:
                await redis_client.setex(cache_key, 60, str(price))
            except Exception as e:
                logger.warning(f"Redis set error: {e}")
        
        return price

    @staticmethod
    async def search_stocks(query: str) -> List[Dict[str, Any]]:
        """
        搜尋股票 - 整合完整股票清單管理器
        支援：
        - 台灣上市/上櫃所有股票（2000+ 檔）
        - 美股主流股票
        - 模糊搜尋代號和名稱
        """
        results = []
        query = query.strip().upper()
        
        if not query:
            return results
        
        # 🎯 優先從完整股票清單搜尋（台股 2000+ 檔）
        try:
            matched_stocks = await stock_list_manager.search_stocks(query, limit=10)
            logger.info(f"🔍 從股票清單找到 {len(matched_stocks)} 檔: {query}")
            
            # 對找到的每一檔，嘗試從 Yahoo Finance 獲取即時價格
            for stock in matched_stocks:
                symbol = stock['symbol']
                try:
                    # 嘗試獲取即時價格
                    price = await YahooFinanceService.get_stock_price(symbol)
                    info = await YahooFinanceService.get_stock_info(symbol)
                    
                    if info:
                        results.append(info)
                    elif price:
                        # 如果只有價格，用基本資訊
                        results.append({
                            'symbol': symbol,
                            'name': stock['name'],
                            'market': stock['market'],
                            'price': price
                        })
                    else:
                        # 即使沒有即時價格，也加入結果（讓用戶知道這檔股票存在）
                        results.append({
                            'symbol': symbol,
                            'name': stock['name'],
                            'market': stock['market'],
                            'price': 0.0  # 標記為無價格
                        })
                        logger.warning(f"⚠️ {symbol} 找不到價格，但股票存在")
                except Exception as e:
                    logger.debug(f"無法獲取 {symbol} 價格: {e}")
                    # 仍然加入結果
                    results.append({
                        'symbol': symbol,
                        'name': stock['name'],
                        'market': stock['market'],
                        'price': 0.0
                    })
        except Exception as e:
            logger.error(f"股票清單搜尋失敗: {e}")
        
        # 📌 Fallback: 如果還是找不到，嘗試直接查 Yahoo Finance
        if not results:
            logger.info(f"⚙️ Fallback to direct Yahoo Finance query: {query}")
            symbols_to_try = []
            
            # 台股代號邏輯
            if query.isdigit():
                symbols_to_try.append(f"{query}.TW")
                symbols_to_try.append(f"{query}.TWO")
            elif ".TW" in query or ".TWO" in query:
                symbols_to_try.append(query)
            else:
                symbols_to_try.append(query)
            
            for symbol in symbols_to_try:
                try:
                    info = await YahooFinanceService.get_stock_info(symbol)
                    if info and info.get('price'):
                        if not any(r['symbol'] == info['symbol'] for r in results):
                            results.append(info)
                            if ".TW" in symbol:
                                break
                except Exception as e:
                    logger.debug(f"Could not fetch {symbol}: {e}")
        
        # 🔧 最終 Fallback: Mock data
        if not results:
            logger.info(f"⚠️ Final fallback to MOCK_STOCKS: {query}")
            for mock_symbol, mock_data in MOCK_STOCKS.items():
                if (query in mock_symbol or 
                    query in mock_data['name'] or
                    mock_symbol.replace('.TW', '').replace('.TWO', '') == query):
                    results.append({
                        'symbol': mock_symbol,
                        'name': mock_data['name'],
                        'market': mock_data['market'],
                        'sector': mock_data.get('sector'),
                        'price': mock_data['price']
                    })
        
        logger.info(f"✅ 搜尋 '{query}' 返回 {len(results)} 檔股票")
        return results

    @staticmethod
    async def get_historical_data(
        symbol: str, 
        period: str = "1mo", 
        interval: str = "1d",
        db: Optional[AsyncSession] = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical data for charts
        多層策略: DB Cache -> yfinance API -> Web Scraper -> Mock Data
        """
        # 計算需要的日期範圍
        end_date = date.today()
        days_map = {"1d": 2, "5d": 7, "1mo": 35, "3mo": 100, "1y": 380}
        days = days_map.get(period, 35)
        start_date = end_date - timedelta(days=days)
        
        # 第一層：檢查資料庫緩存
        if db:
            try:
                from apps.models.historical_price import HistoricalPrice
                
                stmt = select(HistoricalPrice).where(
                    and_(
                        HistoricalPrice.symbol == symbol,
                        HistoricalPrice.date >= start_date,
                        HistoricalPrice.date <= end_date
                    )
                ).order_by(HistoricalPrice.date)
                
                result = await db.execute(stmt)
                cached_data = result.scalars().all()
                
                # 如果緩存數據足夠新（最近3天內有數據）
                if cached_data:
                    latest_date = max(d.date for d in cached_data)
                    days_old = (end_date - latest_date).days
                    
                    if days_old <= 3 and len(cached_data) >= (days * 0.8):  # 至少有80%的數據
                        logger.info(f"✅ DB Cache hit: {len(cached_data)} records for {symbol} (latest: {latest_date})")
                        return [
                            {
                                "date": d.date.isoformat() + "T00:00:00",
                                "open": d.open,
                                "high": d.high,
                                "low": d.low,
                                "close": d.close,
                                "volume": d.volume
                            }
                            for d in cached_data
                        ]
                    else:
                        logger.info(f"⚠️ DB Cache stale: latest={latest_date}, days_old={days_old}")
            except Exception as e:
                logger.warning(f"⚠️ DB Cache read error: {str(e)}")
        
        # 第二層：根據市場選擇數據源
        data = None
        is_taiwan_stock = ".TW" in symbol or ".TWO" in symbol
        
        # 台股優先使用 Fugle → TWSE → FinMind
        if is_taiwan_stock:
            # 2-1. 嘗試 Fugle API（即時 + 歷史數據）
            if FUGLE_AVAILABLE and not data:
                try:
                    start_str = start_date.strftime('%Y-%m-%d')
                    end_str = end_date.strftime('%Y-%m-%d')
                    fugle_data = await fugle_service.get_historical_candles(
                        symbol, 
                        start_date=start_str,
                        end_date=end_str
                    )
                    if fugle_data:
                        # 轉換 Fugle 格式為標準格式
                        data = [
                            {
                                "date": item['date'] + "T00:00:00" if 'T' not in item['date'] else item['date'],
                                "open": float(item['open']),
                                "high": float(item['high']),
                                "low": float(item['low']),
                                "close": float(item['close']),
                                "volume": int(item['volume'])
                            }
                            for item in fugle_data
                        ]
                        logger.info(f"✅ Fugle API success: {len(data)} records for {symbol}")
                except Exception as e:
                    logger.warning(f"⚠️ Fugle API failed for {symbol}: {str(e)}")
            
            # 2-2. Fugle 失敗，嘗試 TWSE 官方 API
            if TAIWAN_SOURCES_AVAILABLE and not data:
                try:
                    start_str = start_date.strftime('%Y%m%d')
                    end_str = end_date.strftime('%Y%m%d')
                    data = TWSEService.get_historical_data(symbol, start_str, end_str)
                    if data:
                        logger.info(f"✅ TWSE API success: {len(data)} records for {symbol}")
                except Exception as e:
                    logger.warning(f"⚠️ TWSE API failed for {symbol}: {str(e)}")
            
            # 2-3. TWSE 失敗，嘗試 FinMind
            if TAIWAN_SOURCES_AVAILABLE and not data:
                try:
                    start_str = start_date.strftime('%Y-%m-%d')
                    end_str = end_date.strftime('%Y-%m-%d')
                    data = FinMindService.get_historical_data(symbol, start_str, end_str)
                    if data:
                        logger.info(f"✅ FinMind API success: {len(data)} records for {symbol}")
                except Exception as e:
                    logger.warning(f"⚠️ FinMind API failed for {symbol}: {str(e)}")
        
        # 第三層：美股優先嘗試 Alpha Vantage（台股跳過）
        if not data and not is_taiwan_stock and ALPHA_VANTAGE_AVAILABLE:
            try:
                # Alpha Vantage 只支援 compact (100天) 或 full (20年)
                outputsize = 'full' if period in ['1y', '3mo'] else 'compact'
                av_data = await alpha_vantage_service.get_daily_data(symbol, outputsize)
                if av_data:
                    # 根據 period 過濾數據
                    data = av_data[-days:] if len(av_data) > days else av_data
                    logger.info(f"✅ Alpha Vantage API success: {len(data)} records for {symbol}")
            except Exception as e:
                logger.warning(f"⚠️ Alpha Vantage API failed for {symbol}: {str(e)}")
        
        # 第四層：嘗試 yfinance API（台股備援或美股備援）
        if not data:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period, interval=interval)
                
                if not hist.empty:
                    hist = hist.reset_index()
                    data = []
                    for _, row in hist.iterrows():
                        date_val = row['Date']
                        if hasattr(date_val, 'isoformat'):
                            date_str = date_val.isoformat()
                        else:
                            date_str = str(date_val)

                        data.append({
                            "date": date_str,
                            "open": float(row["Open"]),
                            "high": float(row["High"]),
                            "low": float(row["Low"]),
                            "close": float(row["Close"]),
                            "volume": int(row["Volume"])
                        })
                    logger.info(f"✅ yfinance API success: {len(data)} records for {symbol}")
            except Exception as e:
                logger.warning(f"⚠️ yfinance API failed for {symbol}: {str(e)}")
        
        # 第五層：嘗試網頁爬蟲
        if not data:
            logger.info(f"🔄 Trying web scraper for {symbol}...")
            data = YahooFinanceService._scrape_historical_data(symbol, period)
            if data:
                logger.info(f"✅ Web scraper success: {len(data)} records for {symbol}")
        
        # 第六層：使用 Mock Data
        if not data:
            logger.warning(f"⚠️ All data sources failed for {symbol}, using mock data")
            data = YahooFinanceService._get_mock_historical_data(symbol, period)
        
        # 保存到資料庫緩存（如果有 db session 且數據不是 mock）
        if db and data and not (symbol in MOCK_STOCKS or any(d.get('is_mock') for d in data)):
            try:
                from apps.models.historical_price import HistoricalPrice
                from sqlalchemy.dialects.postgresql import insert
                
                for d in data:
                    date_obj = datetime.fromisoformat(d['date']).date()
                    
                    stmt = insert(HistoricalPrice).values(
                        symbol=symbol,
                        date=date_obj,
                        open=d['open'],
                        high=d['high'],
                        low=d['low'],
                        close=d['close'],
                        volume=d['volume']
                    ).on_conflict_do_update(
                        index_elements=['symbol', 'date'],
                        set_={
                            'open': d['open'],
                            'high': d['high'],
                            'low': d['low'],
                            'close': d['close'],
                            'volume': d['volume'],
                            'updated_at': datetime.utcnow()
                        }
                    )
                    await db.execute(stmt)
                
                await db.commit()
                logger.info(f"💾 Saved {len(data)} records to DB cache for {symbol}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to save to DB cache: {str(e)}")
                await db.rollback()
        
        return data

    @staticmethod
    def _get_mock_historical_data(symbol: str, period: str = "1mo") -> List[Dict[str, Any]]:
        """
        Generate mock historical data for testing
        根據 MOCK_STOCKS 的當前價格生成合理的歷史數據
        """
        from datetime import timedelta
        import random
        
        # Determine number of data points based on period
        days_map = {
            "1d": 1,
            "5d": 5,
            "1mo": 30,
            "3mo": 90,
            "6mo": 180,
            "1y": 365
        }
        days = days_map.get(period, 30)
        
        # 使用 MOCK_STOCKS 中的實際價格作為最新價格
        if symbol in MOCK_STOCKS:
            latest_price = MOCK_STOCKS[symbol]["price"]
        else:
            # 嘗試不帶後綴的股票代碼
            base_symbol = symbol.replace(".TW", "").replace(".TWO", "")
            tw_symbol = f"{base_symbol}.TW"
            if tw_symbol in MOCK_STOCKS:
                latest_price = MOCK_STOCKS[tw_symbol]["price"]
            else:
                latest_price = 500.0 if ".TW" in symbol else 150.0
        
        data = []
        current_date = datetime.utcnow() - timedelta(days=days)
        
        # 從較低的價格開始,逐步上漲到當前價格 (模擬上漲趨勢)
        start_price = latest_price * 0.90  # 從 90% 的價格開始
        
        for i in range(days):
            # 線性插值 + 隨機波動
            progress = i / (days - 1) if days > 1 else 1
            base_price = start_price + (latest_price - start_price) * progress
            
            # 添加隨機波動 (-2% to +2%)
            daily_change = random.uniform(-0.02, 0.02)
            current_price = base_price * (1 + daily_change)
            
            open_price = current_price * random.uniform(0.995, 1.005)
            high_price = current_price * random.uniform(1.005, 1.02)
            low_price = current_price * random.uniform(0.98, 0.995)
            close_price = current_price
            volume = random.randint(10000000, 50000000)
            
            data.append({
                "date": (current_date + timedelta(days=i)).isoformat(),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": volume
            })
        
        # 確保最後一天的收盤價等於 latest_price
        if data:
            data[-1]["close"] = latest_price
            data[-1]["open"] = round(latest_price * 0.998, 2)
            data[-1]["high"] = round(latest_price * 1.01, 2)
            data[-1]["low"] = round(latest_price * 0.99, 2)
        
        return data
