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
    db: AsyncSession = Depends(get_db)
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


@router.get("/sentiment-stats")
async def get_sentiment_stats(
    symbol: str,
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """
    Get sentiment statistics for a stock
    
    Returns:
    - total_news: Total news count
    - positive_count: Number of positive news
    - negative_count: Number of negative news
    - neutral_count: Number of neutral news
    - positive_ratio: Percentage of positive news
    - negative_ratio: Percentage of negative news
    - avg_sentiment_score: Average sentiment score (-1 to 1)
    - sentiment_index: Overall sentiment index (0-100, 50=neutral)
    """
    try:
        from sqlalchemy import func
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all news with sentiment scores
        stmt = select(
            StockNews.sentiment,
            StockNews.sentiment_score
        ).where(
            and_(
                StockNews.symbol == symbol,
                StockNews.published_at >= cutoff_date
            )
        )
        
        result = await db.execute(stmt)
        news_list = result.all()
        
        if not news_list:
            return {
                "symbol": symbol,
                "days": days,
                "total_news": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "positive_ratio": 0,
                "negative_ratio": 0,
                "avg_sentiment_score": 0,
                "sentiment_index": 50,
                "sentiment_label": "中性"
            }
        
        # Calculate statistics
        total = len(news_list)
        positive = sum(1 for s, _ in news_list if s == 'positive')
        negative = sum(1 for s, _ in news_list if s == 'negative')
        neutral = sum(1 for s, _ in news_list if s == 'neutral')
        
        # Calculate average score (only non-neutral)
        scores = [score for _, score in news_list if score != 0]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Calculate sentiment index (0-100, 50=neutral)
        # Formula: 50 + (avg_score * 50)
        sentiment_index = 50 + (avg_score * 50)
        
        # Determine sentiment label
        if sentiment_index >= 65:
            sentiment_label = "強烈利多"
        elif sentiment_index >= 55:
            sentiment_label = "偏多"
        elif sentiment_index <= 35:
            sentiment_label = "強烈利空"
        elif sentiment_index <= 45:
            sentiment_label = "偏空"
        else:
            sentiment_label = "中性"
        
        # Generate AI summary reasons for positive/negative sentiment
        positive_reasons = []
        negative_reasons = []
        
        # Get positive news titles for AI analysis
        if positive > 0:
            stmt_positive = select(StockNews.title).where(
                and_(
                    StockNews.symbol == symbol,
                    StockNews.published_at >= cutoff_date,
                    StockNews.sentiment == 'positive',
                    StockNews.sentiment_score > 0.5
                )
            ).limit(5)
            result_positive = await db.execute(stmt_positive)
            positive_titles = [row[0] for row in result_positive.all()]
            
            if positive_titles:
                # Use Gemini AI to generate summary
                prompt = f"""分析以下關於 {symbol} 的利多新聞，提取3個最重要的利多原因，每個原因用一句話簡潔說明（15-30字）:

{chr(10).join(f'{i+1}. {title}' for i, title in enumerate(positive_titles))}

請直接列出3個原因，不要編號，每行一個原因。"""
                
                try:
                    summary = await gemini_service.generate_text(prompt)
                    if summary:
                        # Split by newlines and clean up
                        reasons = [r.strip() for r in summary.split('\n') if r.strip()]
                        # Remove numbering if exists
                        reasons = [r.lstrip('0123456789.-) ') for r in reasons]
                        positive_reasons = [r for r in reasons if r][:3]
                except Exception as e:
                    logger.warning(f"Failed to generate positive summary: {e}")
                    positive_reasons = [title[:40] + '...' for title in positive_titles[:3]]
        
        # Get negative news titles for AI analysis  
        if negative > 0:
            stmt_negative = select(StockNews.title).where(
                and_(
                    StockNews.symbol == symbol,
                    StockNews.published_at >= cutoff_date,
                    StockNews.sentiment == 'negative',
                    StockNews.sentiment_score < -0.5
                )
            ).limit(5)
            result_negative = await db.execute(stmt_negative)
            negative_titles = [row[0] for row in result_negative.all()]
            
            if negative_titles:
                # Use Gemini AI to generate summary
                prompt = f"""分析以下關於 {symbol} 的利空新聞，提取3個最重要的利空原因，每個原因用一句話簡潔說明（15-30字）:

{chr(10).join(f'{i+1}. {title}' for i, title in enumerate(negative_titles))}

請直接列出3個原因，不要編號，每行一個原因。"""
                
                try:
                    summary = await gemini_service.generate_text(prompt)
                    if summary:
                        # Split by newlines and clean up
                        reasons = [r.strip() for r in summary.split('\n') if r.strip()]
                        # Remove numbering if exists
                        reasons = [r.lstrip('0123456789.-) ') for r in reasons]
                        negative_reasons = [r for r in reasons if r][:3]
                except Exception as e:
                    logger.warning(f"Failed to generate negative summary: {e}")
                    negative_reasons = [title[:40] + '...' for title in negative_titles[:3]]
        
        return {
            "symbol": symbol,
            "days": days,
            "total_news": total,
            "positive_count": positive,
            "negative_count": negative,
            "neutral_count": neutral,
            "positive_ratio": round(positive / total * 100, 1) if total > 0 else 0,
            "negative_ratio": round(negative / total * 100, 1) if total > 0 else 0,
            "avg_sentiment_score": round(avg_score, 2),
            "sentiment_index": round(sentiment_index, 1),
            "sentiment_label": sentiment_label,
            "positive_reasons": positive_reasons,
            "negative_reasons": negative_reasons
        }
        
    except Exception as e:
        logger.error(f"Error calculating sentiment stats for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate sentiment statistics")


@router.post("/fetch")
async def fetch_stock_news(
    symbol: str,
    db: AsyncSession = Depends(get_db)
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


@router.post("/reanalyze")
async def reanalyze_news(
    symbol: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Re-analyze sentiment for all neutral news of a stock
    
    - symbol: Stock symbol
    """
    try:
        if not gemini_service.is_available():
            raise HTTPException(status_code=503, detail="AI service not available")
        
        # Get all neutral news for this stock
        stmt = select(StockNews).where(
            and_(
                StockNews.symbol == symbol,
                StockNews.sentiment == 'neutral'
            )
        )
        result = await db.execute(stmt)
        news_list = result.scalars().all()
        
        if not news_list:
            return {
                "symbol": symbol,
                "reanalyzed": 0,
                "message": "No neutral news found"
            }
        
        reanalyzed_count = 0
        for news in news_list:
            try:
                sentiment_data = await gemini_service.analyze_news_sentiment(
                    title=news.title,
                    summary=news.summary or ''
                )
                news.sentiment = sentiment_data['sentiment']
                news.sentiment_score = sentiment_data['sentiment_score']
                reanalyzed_count += 1
                logger.info(f"Reanalyzed: {news.title[:50]} -> {news.sentiment} ({news.sentiment_score})")
            except Exception as e:
                logger.error(f"Failed to reanalyze news {news.id}: {e}")
                continue
        
        await db.commit()
        
        return {
            "symbol": symbol,
            "total_neutral": len(news_list),
            "reanalyzed": reanalyzed_count,
            "message": f"Successfully reanalyzed {reanalyzed_count} news items"
        }
        
    except Exception as e:
        logger.error(f"Error reanalyzing news for {symbol}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to reanalyze news: {str(e)}")
