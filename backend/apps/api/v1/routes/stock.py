from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
from apps.core.database import get_db
from apps.core.services.yahoo_finance import YahooFinanceService
from apps.core.services.technical_indicators import TechnicalIndicatorService
from apps.schemas.stock import StockResponse
from apps.models.stock import Stock
from apps.core.dependencies import get_current_user
from apps.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Stocks"])

@router.get("/stocks/search", response_model=List[StockResponse])
async def search_stocks(
    q: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search for stocks by symbol or name using Yahoo Finance
    """
    if not q:
        return []
    
    # 1. Search via Yahoo Finance Service
    results = await YahooFinanceService.search_stocks(q)
    
    # 2. (Optional) Save found stocks to local DB for caching/reference
    for info in results:
        symbol = info['symbol']
        # Check if exists
        stmt = select(Stock).where(Stock.symbol == symbol)
        result = await db.execute(stmt)
        existing_stock = result.scalars().first()
        
        if not existing_stock:
            new_stock = Stock(
                symbol=symbol,
                name=info.get('name', 'Unknown'),
                market=info.get('market', 'Unknown'),
                sector=info.get('sector')
            )
            db.add(new_stock)
            try:
                await db.commit()
            except Exception:
                await db.rollback()
    
    return results

@router.get("/stocks/{symbol}")
async def get_stock_quote(
    symbol: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get real-time quote for a stock (包含漲跌數據)
    """
    logger.info(f"🔍 Received request for stock: {symbol}")
    
    # 1. Get info from Yahoo Finance (includes price)
    info = await YahooFinanceService.get_stock_info(symbol)
    
    if not info:
        logger.error(f"❌ Stock {symbol} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Stock {symbol} not found"
        )
    
    logger.info(f"📊 Initial info: price={info.get('price')}, change={info.get('change')}, change_percent={info.get('change_percent')}")
    
    # 2. 如果 change 和 change_percent 為 None,從歷史數據計算
    if info.get('change') is None or info.get('change_percent') is None:
        try:
            logger.info(f"⚠️ Change data missing for {symbol}, calculating from history...")
            # 獲取最近2天的數據來計算漲跌
            hist_data = await YahooFinanceService.get_historical_data(symbol, '5d', '1d', db)
            logger.info(f"📈 Historical data length: {len(hist_data) if hist_data else 0}")
            
            if hist_data and len(hist_data) >= 2:
                today_price = hist_data[-1].get('close')
                yesterday_price = hist_data[-2].get('close')
                
                logger.info(f"📅 Yesterday: {yesterday_price}, Today: {today_price}")
                
                if today_price and yesterday_price and yesterday_price > 0:
                    change = today_price - yesterday_price
                    change_percent = (change / yesterday_price) * 100
                    
                    info['change'] = round(change, 2)
                    info['change_percent'] = round(change_percent, 2)
                    info['price'] = today_price  # 確保價格是最新的
                    
                    logger.info(f"✅ Calculated change for {symbol}: {change:.2f} ({change_percent:.2f}%)")
                else:
                    logger.warning(f"⚠️ Invalid price data: today={today_price}, yesterday={yesterday_price}")
            else:
                logger.warning(f"⚠️ Not enough historical data for {symbol}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to calculate change for {symbol}: {e}")
            # 設置預設值避免前端顯示 null
            if info.get('change') is None:
                info['change'] = 0.0
            if info.get('change_percent') is None:
                info['change_percent'] = 0.0
    
    logger.info(f"📤 Returning {symbol}: price={info.get('price')}, change={info.get('change')}, change_percent={info.get('change_percent')}")
    return info


@router.get("/stocks/{symbol}/history")
async def get_stock_history(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get historical price data for charting
    支援資料庫緩存，減少 API 調用
    
    Parameters:
    - period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    - interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
    """
    try:
        data = await YahooFinanceService.get_historical_data(symbol, period, interval, db)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch historical data: {str(e)}"
        )


@router.get("/stocks/{symbol}/indicators")
async def get_technical_indicators(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get technical indicators for stock analysis
    追溯: US-03, FR-04
    支援資料庫快取
    
    Parameters:
    - period: 1d, 5d, 1mo, 3mo, 6mo, 1y
    - interval: 1d (only daily supported for now)
    
    Returns:
    - MA (5, 10, 20, 60 day)
    - MACD (12, 26, 9)
    - RSI (14)
    - KDJ (9, 3)
    """
    try:
        # Get historical data with DB caching
        hist_data = await YahooFinanceService.get_historical_data(symbol, period, interval, db)
        
        if not hist_data:
            return {"indicators": {}, "message": "No historical data available"}
        
        # Calculate all indicators
        indicators = TechnicalIndicatorService.calculate_all_indicators(hist_data)
        
        return {
            "symbol": symbol,
            "period": period,
            "data_points": len(hist_data),
            "indicators": indicators
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate indicators: {str(e)}"
        )
