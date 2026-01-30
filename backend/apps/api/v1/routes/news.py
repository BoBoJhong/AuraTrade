from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from apps.core.database import get_db
from apps.models.stock_news import StockNews
from apps.models.user import User
from apps.core.dependencies import get_current_user
from apps.core.services.google_news_service import GoogleNewsService
from apps.core.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stocks/{symbol}/news", tags=["news"])

@router.get("")
async def get_stock_news(
    symbol: str,
    limit: int = Query(20, ge=1, le=100),
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Query stock news
    
    - symbol: Stock symbol
    - limit: Max results to return
    - days: Query news from last N days
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        stmt = select(StockNews).where(
            and_(
                StockNews.symbol == symbol,
                StockNews.published_at >= cutoff_date
            )
        ).order_by(desc(StockNews.published_at)).limit(limit)
        
        result = await db.execute(stmt)
        news_items = result.scalars().all()
        
        return {
            "symbol": symbol,
            "count": len(news_items),
            "news": [
                {
                    "id": news.id,
                    "title": news.title,
                    "summary": news.summary,
                    "source": news.source,
                    "url": news.url,
                    "published_at": news.published_at.isoformat(),
                    "sentiment": news.sentiment,
                    "sentiment_score": news.sentiment_score
                }
                for news in news_items
            ]
        }
        
    except Exception as e:
        logger.error(f"Error querying news for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to query news")


@router.post("/fetch")
async def fetch_stock_news(
    symbol: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually fetch latest news for a stock
    
    - symbol: Stock symbol
    """
    try:
        # Initialize services
        news_service = GoogleNewsService()
        
        # Get stock name (simplified mapping)
        stock_names = {
            "2330.TW": "TSMC",
            "2317.TW": "Hon Hai",
            "2454.TW": "MediaTek",
            "2308.TW": "Delta Electronics",
            "0050.TW": "Taiwan 50",
            "006208.TW": "Fubon NASDAQ",
            "AAPL": "Apple",
            "MSFT": "Microsoft",
            "GOOGL": "Google",
            "TSLA": "Tesla",
            "NVDA": "NVIDIA"
        }
        stock_name = stock_names.get(symbol, symbol)
        
        # Fetch news
        news_items = await news_service.fetch_stock_news(
            symbol=symbol,
            stock_name=stock_name,
            max_results=10
        )
        
        saved_count = 0
        for news_item in news_items:
            # Check if news already exists (by URL)
            existing = await db.execute(
                select(StockNews).where(StockNews.url == news_item['url'])
            )
            if existing.scalar_one_or_none():
                continue
            
            # AI sentiment analysis
            sentiment_data = None
            if gemini_service.is_available():
                sentiment_data = await gemini_service.analyze_news_sentiment(
                    title=news_item['title'],
                    summary=news_item.get('summary', '')
                )
            
            # Save news
            news_obj = StockNews(
                symbol=symbol,
                title=news_item['title'],
                summary=news_item.get('summary', ''),
                content=news_item.get('content', ''),
                source=news_item['source'],
                url=news_item['url'],
                published_at=news_item['published_at'],
                sentiment=sentiment_data['sentiment'] if sentiment_data else 'neutral',
                sentiment_score=sentiment_data['sentiment_score'] if sentiment_data else 0.0
            )
            db.add(news_obj)
            saved_count += 1
        
        await db.commit()
        
        return {
            "symbol": symbol,
            "fetched": len(news_items),
            "saved": saved_count,
            "message": f"Successfully fetched and saved {saved_count} news items"
        }
        
    except Exception as e:
        logger.error(f"Error fetching news for {symbol}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to fetch news: {str(e)}")
