from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
from sqlalchemy import select

from apps.core.database import get_db_context
from apps.models.stock_news import StockNews
from apps.core.services.google_news_service import GoogleNewsService
from apps.core.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

# Stocks to monitor for news
MONITORED_STOCKS = [
    ("2330.TW", "TSMC"),
    ("2317.TW", "Hon Hai"),
    ("2454.TW", "MediaTek"),
    ("2308.TW", "Delta Electronics"),
    ("0050.TW", "Taiwan 50"),
    ("006208.TW", "Fubon NASDAQ"),
    ("AAPL", "Apple"),
    ("MSFT", "Microsoft"),
    ("GOOGL", "Google"),
    ("TSLA", "Tesla"),
    ("NVDA", "NVIDIA")
]

class NewsScheduler:
    """Scheduler for automated news fetching"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.news_service = GoogleNewsService()
    
    async def fetch_and_save_stock_news(self, symbol: str, stock_name: str):
        """Fetch and save news for a single stock"""
        try:
            logger.info(f"Fetching news for {symbol} ({stock_name})...")
            
            # Fetch news
            news_items = await self.news_service.fetch_stock_news(
                symbol=symbol,
                stock_name=stock_name,
                max_results=5
            )
            
            if not news_items:
                logger.info(f"No news found for {symbol}")
                return
            
            # Save to database
            async with get_db_context() as db:
                saved_count = 0
                for news_item in news_items:
                    # Check if exists
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
                logger.info(f"Saved {saved_count} news items for {symbol}")
                
        except Exception as e:
            logger.error(f"Failed to fetch news for {symbol}: {e}")
    
    async def fetch_all_monitored_stocks(self):
        """Fetch news for all monitored stocks"""
        logger.info("Starting scheduled news fetch for all monitored stocks...")
        
        for symbol, stock_name in MONITORED_STOCKS:
            try:
                await self.fetch_and_save_stock_news(symbol, stock_name)
            except Exception as e:
                logger.error(f"Error fetching news for {symbol}: {e}")
        
        logger.info("Completed scheduled news fetch")
    
    def start(self):
        """Start the scheduler"""
        # Schedule hourly news fetch (at minute 5 of every hour)
        self.scheduler.add_job(
            self.fetch_all_monitored_stocks,
            CronTrigger(minute=5),
            id='hourly_news_fetch',
            name='Fetch stock news every hour',
            replace_existing=True
        )
        
        # Add startup job (fetch immediately after 30 seconds)
        self.scheduler.add_job(
            self.fetch_all_monitored_stocks,
            'date',
            run_date=datetime.now(),
            id='startup_news_fetch',
            name='Initial news fetch on startup'
        )
        
        self.scheduler.start()
        logger.info("News scheduler started successfully")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("News scheduler stopped")

# Global instance
news_scheduler = NewsScheduler()
