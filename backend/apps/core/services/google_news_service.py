import httpx
import feedparser
from datetime import datetime
from dateutil import parser as date_parser
import re
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class GoogleNewsService:
    """Google News RSS Feed Service for stock news"""
    
    def __init__(self):
        self.base_url = "https://news.google.com/rss/search"
        self.timeout = 30
    
    async def fetch_stock_news(
        self,
        symbol: str,
        stock_name: str,
        language: str = "zh-TW",
        max_results: int = 20
    ) -> List[Dict]:
        """
        Fetch news for a specific stock
        
        Args:
            symbol: Stock symbol (e.g., 2330.TW, AAPL)
            stock_name: Stock full name (e.g., TSMC, Apple)
            language: Language code (zh-TW, en)
            max_results: Maximum number of results
        
        Returns:
            List of news items with title, summary, url, published_at
        """
        try:
            # Remove .TW/.TWO suffix for search
            search_symbol = symbol.replace('.TW', '').replace('.TWO', '')
            
            # Build query: stock name + stock symbol
            query = f"{stock_name} {search_symbol}"
            
            # Request parameters
            params = {
                "q": query,
                "hl": language,
                "gl": "TW" if language == "zh-TW" else "US",
                "ceid": "TW:zh-Hant" if language == "zh-TW" else "US:en"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                
                # Parse RSS feed
                feed = feedparser.parse(response.text)
                
                news_items = []
                for entry in feed.entries[:max_results]:
                    try:
                        news_item = {
                            "title": entry.get("title", ""),
                            "summary": self._clean_html(entry.get("summary", "")),
                            "content": self._clean_html(entry.get("description", "")),
                            "source": entry.get("source", {}).get("title", "Google News"),
                            "url": entry.get("link", ""),
                            "published_at": self._parse_datetime(entry.get("published", ""))
                        }
                        news_items.append(news_item)
                    except Exception as e:
                        logger.warning(f"Failed to parse news entry: {e}")
                        continue
                
                logger.info(f"Fetched {len(news_items)} news items for {symbol}")
                return news_items
                
        except Exception as e:
            logger.error(f"Failed to fetch news for {symbol}: {e}")
            return []
    
    async def fetch_market_news(
        self,
        market: str = "Taiwan",
        topics: List[str] = None,
        language: str = "zh-TW",
        max_results: int = 20
    ) -> List[Dict]:
        """
        Fetch general market news
        
        Args:
            market: Market name (Taiwan, US, etc.)
            topics: List of topics to search
            language: Language code
            max_results: Maximum number of results
        
        Returns:
            List of news items
        """
        if topics is None:
            topics = ["stock market", "economy", "finance"]
        
        query = f"{market} {' '.join(topics)}"
        
        try:
            params = {
                "q": query,
                "hl": language,
                "gl": "TW" if language == "zh-TW" else "US",
                "ceid": "TW:zh-Hant" if language == "zh-TW" else "US:en"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                
                feed = feedparser.parse(response.text)
                
                news_items = []
                for entry in feed.entries[:max_results]:
                    try:
                        news_item = {
                            "title": entry.get("title", ""),
                            "summary": self._clean_html(entry.get("summary", "")),
                            "content": self._clean_html(entry.get("description", "")),
                            "source": entry.get("source", {}).get("title", "Google News"),
                            "url": entry.get("link", ""),
                            "published_at": self._parse_datetime(entry.get("published", ""))
                        }
                        news_items.append(news_item)
                    except Exception as e:
                        logger.warning(f"Failed to parse news entry: {e}")
                        continue
                
                logger.info(f"Fetched {len(news_items)} market news items")
                return news_items
                
        except Exception as e:
            logger.error(f"Failed to fetch market news: {e}")
            return []
    
    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from text"""
        if not text:
            return ""
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', text)
        # Remove extra whitespace
        clean_text = ' '.join(clean_text.split())
        return clean_text
    
    def _parse_datetime(self, date_str: str) -> datetime:
        """Parse datetime string from RSS feed"""
        try:
            return date_parser.parse(date_str)
        except Exception as e:
            logger.warning(f"Failed to parse date {date_str}: {e}")
            return datetime.utcnow()
