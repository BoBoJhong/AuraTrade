"""
Stock Screener API
智能選股器功能 - 根據技術指標和基本面篩選股票
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
from apps.core.dependencies import get_current_user, get_db
from apps.models.user import User
from apps.core.services.yahoo_finance import YahooFinanceService
from apps.core.services.technical_indicators import TechnicalIndicatorService
from apps.core.services.stock_list_manager import stock_list_manager
from apps.core.services.google_news_service import GoogleNewsService
from apps.core.services.alpha_vantage_service import alpha_vantage_service
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Screener"])


@router.get("/screener")
async def screen_stocks(
    # 篩選條件
    min_price: Optional[float] = Query(None, description="最低股價"),
    max_price: Optional[float] = Query(None, description="最高股價"),
    min_market_cap: Optional[float] = Query(None, description="最低市值 (億)"),
    max_market_cap: Optional[float] = Query(None, description="最高市值 (億)"),
    min_pe_ratio: Optional[float] = Query(None, description="最低本益比"),
    max_pe_ratio: Optional[float] = Query(None, description="最高本益比"),
    min_dividend_yield: Optional[float] = Query(None, description="最低殖利率 (%)"),
    max_dividend_yield: Optional[float] = Query(None, description="最高殖利率 (%)"),
    min_volume: Optional[int] = Query(None, description="最低成交量"),
    
    # 技術指標篩選
    rsi_min: Optional[float] = Query(None, description="RSI 最小值 (0-100)"),
    rsi_max: Optional[float] = Query(None, description="RSI 最大值 (0-100)"),
    
    # 分頁
    limit: int = Query(50, le=200, description="返回數量"),
    
    db: AsyncSession = Depends(get_db)
):
    """
    智能選股器
    
    根據價格、市值、本益比、殖利率、技術指標等條件篩選股票
    """
    try:
        # 獲取完整股票列表（台股 2000+ 檔 + 美股）
        all_stocks = await stock_list_manager.get_all_stocks()
        
        # 使用完整市場作為候選池（考慮效能，限制前 500 檔 + 美股）
        stock_symbols = [s['symbol'] for s in all_stocks[:500]]  # 台股前 500 大市值
        stock_symbols.extend([  # 加入主流美股
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA",
            "NFLX", "AMD", "INTC", "CSCO", "ADBE", "CRM", "ORCL",
            "QCOM", "TXN", "AVGO", "BABA", "TSM", "ASML"
        ])
        
        logger.info(f"🔍 篩選範圍: {len(stock_symbols)} 檔股票")
        
        matched_stocks = []
        
        for symbol in stock_symbols:
            try:
                # 獲取股票即時報價
                quote = await YahooFinanceService.get_stock_info(symbol)
                if not quote:
                    continue
                
                # 獲取價格
                current_price = quote.get('price', 0)
                if not current_price:
                    continue
                
                # 價格篩選
                if min_price is not None and current_price < min_price:
                    continue
                if max_price is not None and current_price > max_price:
                    continue
                
                # 市值篩選 (單位：億)
                market_cap = quote.get('market_cap', 0)
                market_cap_yi = 0
                if market_cap:
                    market_cap_yi = market_cap / 100000000  # 轉換為億
                    if min_market_cap is not None and market_cap_yi < min_market_cap:
                        continue
                    if max_market_cap is not None and market_cap_yi > max_market_cap:
                        continue
                
                # 本益比篩選
                pe_ratio = quote.get('pe_ratio')
                if pe_ratio:
                    if min_pe_ratio is not None and pe_ratio < min_pe_ratio:
                        continue
                    if max_pe_ratio is not None and pe_ratio > max_pe_ratio:
                        continue
                
                # 殖利率篩選
                dividend_yield = quote.get('dividend_yield')
                if dividend_yield:
                    if min_dividend_yield is not None and dividend_yield < min_dividend_yield:
                        continue
                    if max_dividend_yield is not None and dividend_yield > max_dividend_yield:
                        continue
                
                # 成交量篩選
                volume = quote.get('volume', 0)
                if min_volume is not None and volume < min_volume:
                    continue
                
                # 技術指標篩選 (RSI)
                if rsi_min is not None or rsi_max is not None:
                    hist_data = await YahooFinanceService.get_historical_data(symbol, "1mo", "1d", db)
                    if hist_data:
                        rsi_values = TechnicalIndicatorService.calculate_rsi(hist_data, 14)
                        if rsi_values and len(rsi_values) > 0:
                            latest_rsi = [r for r in rsi_values if r is not None][-1] if any(r is not None for r in rsi_values) else None
                            if latest_rsi:
                                if rsi_min is not None and latest_rsi < rsi_min:
                                    continue
                                if rsi_max is not None and latest_rsi > rsi_max:
                                    continue
                
                # 符合條件，加入結果
                matched_stocks.append({
                    "symbol": symbol,
                    "name": quote.get('name', symbol),
                    "price": current_price,
                    "change": quote.get('change', 0),
                    "change_percent": quote.get('change_percent', 0),
                    "volume": volume,
                    "market_cap": market_cap_yi,
                    "pe_ratio": pe_ratio,
                    "dividend_yield": dividend_yield
                })
                
                # 達到限制數量就停止
                if len(matched_stocks) >= limit:
                    break
                    
            except Exception as e:
                logger.error(f"Error screening stock {symbol}: {str(e)}")
                continue
        
        return {
            "total": len(matched_stocks),
            "stocks": matched_stocks,
            "filters_applied": {
                "price_range": [min_price, max_price] if min_price or max_price else None,
                "market_cap_range": [min_market_cap, max_market_cap] if min_market_cap or max_market_cap else None,
                "pe_ratio_range": [min_pe_ratio, max_pe_ratio] if min_pe_ratio or max_pe_ratio else None,
                "dividend_yield_range": [min_dividend_yield, max_dividend_yield] if min_dividend_yield or max_dividend_yield else None,
                "rsi_range": [rsi_min, rsi_max] if rsi_min or rsi_max else None
            }
        }
        
    except Exception as e:
        logger.error(f"Stock screener error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Screener failed: {str(e)}"
        )


@router.get("/stocks/trending")
async def get_trending_stocks(
    limit: int = Query(10, le=50, description="返回數量"),
    db: AsyncSession = Depends(get_db)
):
    """
    熱門股票排行榜
    
    快速掃描精選股票，根據成交量排序
    """
    try:
        # 精選熱門股票池
        hot_symbols = [
            # 台股權值股
            "2330.TW", "2317.TW", "2454.TW", "2412.TW", "2308.TW",
            "2882.TW", "2303.TW", "2886.TW", "2891.TW", "2002.TW",
            "0050.TW", "006208.TW", "0056.TW", "2881.TW", "2884.TW",
            # 美股科技股
            "AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "META", "AMZN",
            "NFLX", "AMD", "INTC", "CSCO", "ADBE"
        ]
        
        logger.info(f"🔍 熱門排行快速掃描: {len(hot_symbols)} 檔")
        
        # 快速獲取函數
        async def quick_fetch(symbol: str) -> Optional[Dict]:
            try:
                quote = await YahooFinanceService.get_stock_info(symbol)
                if quote and quote.get('price'):
                    market_cap = quote.get('market_cap', 0)
                    return {
                        "symbol": symbol,
                        "name": quote.get('name', symbol),
                        "price": quote.get('price'),
                        "change": quote.get('change', 0),
                        "change_percent": quote.get('change_percent', 0),
                        "volume": quote.get('volume', 0),
                        "market_cap": market_cap / 100000000 if market_cap else 0
                    }
            except Exception as e:
                logger.error(f"Quick fetch error {symbol}: {str(e)}")
                return None
        
        # 全部併發執行
        results = await asyncio.gather(
            *[quick_fetch(s) for s in hot_symbols], 
            return_exceptions=True
        )
        trending_stocks = [r for r in results if r and not isinstance(r, Exception)]
        
        # 按成交量排序
        trending_stocks.sort(key=lambda x: x['volume'], reverse=True)
        
        logger.info(f"✅ 熱門排行完成: 返回 {len(trending_stocks[:limit])} 檔")
        
        return {
            "total": len(trending_stocks[:limit]),
            "stocks": trending_stocks[:limit]
        }
        
    except Exception as e:
        logger.error(f"Trending error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trending: {str(e)}"
        )


@router.get("/stocks/ai-picks")
async def get_ai_stock_picks(
    limit: int = Query(10, le=50, description="返回數量"),
    db: AsyncSession = Depends(get_db)
):
    """
    AI 智能推薦股票
    
    快速掃描精選股票，基於價格動態和基本面分析
    """
    try:
        # 進一步減少候選池，優先速度
        candidate_symbols = [
            # 台股熱門
            "2330.TW", "2317.TW", "2454.TW", "2412.TW", "2308.TW",
            "0050.TW", "006208.TW", "0056.TW", "2882.TW", "2303.TW",
            # 美股科技
            "AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "AMD", "META", "AMZN",
            "NFLX", "INTC"
        ]
        
        logger.info(f"🔍 AI 快速掃描: {len(candidate_symbols)} 檔精選股票")
        
        # 初始化新聞服務
        google_news = GoogleNewsService()
        
        # 快速分析函數（包含新聞情緒）
        async def quick_analyze(symbol: str) -> Optional[Dict]:
            try:
                quote = await YahooFinanceService.get_stock_info(symbol)
                if not quote or not quote.get('price'):
                    return None
                
                current_price = quote.get('price')
                change_percent = quote.get('change_percent', 0)
                pe_ratio = quote.get('pe_ratio')
                volume = quote.get('volume', 0)
                market_cap = quote.get('market_cap', 0)
                stock_name = quote.get('name', symbol)
                
                # 簡化評分邏輯（不需要歷史數據）
                score = 50
                reasons = []
                news_sentiment = None
                latest_news = []
                
                # 漲跌幅評分
                if -2 < change_percent < 0:
                    score += 15
                    reasons.append("小幅回調，進場機會")
                elif change_percent < -5:
                    score += 20
                    reasons.append("大幅回調，超跌反彈")
                elif change_percent > 5:
                    score -= 10
                    reasons.append("漲幅過大，追高風險")
                elif -0.5 <= change_percent <= 2:
                    score += 5
                    reasons.append("價格穩定")
                
                # 本益比評分
                if pe_ratio:
                    if 10 < pe_ratio < 20:
                        score += 15
                        reasons.append("本益比合理偏低")
                    elif 20 <= pe_ratio < 30:
                        score += 10
                        reasons.append("本益比合理")
                    elif pe_ratio > 50:
                        score -= 10
                        reasons.append("本益比偏高")
                
                # 成交量評分（大於平均視為活躍）
                if volume > 10000000:
                    score += 10
                    reasons.append("成交量活躍")
                
                # 市值評分（大型股較穩定）
                if market_cap and market_cap > 100000000000:  # 1000億以上
                    score += 5
                    reasons.append("大型績優股")
                
                # 新聞情緒評分（優先使用 Alpha Vantage，回退到 Google News）
                try:
                    # 美股優先用 Alpha Vantage
                    if not symbol.endswith('.TW') and not symbol.endswith('.TWO'):
                        av_news = await alpha_vantage_service.get_news_sentiment(
                            tickers=symbol,
                            limit=3
                        )
                        if av_news:
                            sentiment_scores = [n.get('overall_sentiment_score', 0) for n in av_news]
                            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
                            
                            if avg_sentiment > 0.2:  # Bullish
                                score += 15
                                reasons.append("新聞情緒正面")
                                news_sentiment = "正面"
                            elif avg_sentiment < -0.2:  # Bearish
                                score -= 10
                                reasons.append("新聞情緒負面")
                                news_sentiment = "負面"
                            else:
                                news_sentiment = "中性"
                            
                            latest_news = [{
                                "title": n.get('title'),
                                "url": n.get('url'),
                                "sentiment": n.get('overall_sentiment_label')
                            } for n in av_news[:2]]
                    
                    # 台股或 Alpha Vantage 失敗時用 Google News
                    if not latest_news:
                        google_news_items = await google_news.fetch_stock_news(
                            symbol=symbol,
                            stock_name=stock_name,
                            language="zh-TW" if symbol.endswith('.TW') or symbol.endswith('.TWO') else "en",
                            max_results=3
                        )
                        if google_news_items:
                            # 簡單情緒判斷：標題關鍵字
                            positive_keywords = ['增長', '上漲', '突破', '創新高', '買進', 'up', 'surge', 'growth', 'bullish', 'positive']
                            negative_keywords = ['下跌', '虧損', '警告', '風險', '賣出', 'down', 'fall', 'drop', 'bearish', 'negative', 'warning']
                            
                            positive_count = 0
                            negative_count = 0
                            for news in google_news_items:
                                title = news.get('title', '').lower()
                                if any(kw in title for kw in positive_keywords):
                                    positive_count += 1
                                if any(kw in title for kw in negative_keywords):
                                    negative_count += 1
                            
                            if positive_count > negative_count:
                                score += 10
                                reasons.append("新聞偏向正面")
                                news_sentiment = "偏正面"
                            elif negative_count > positive_count:
                                score -= 8
                                reasons.append("新聞偏向負面")
                                news_sentiment = "偏負面"
                            else:
                                news_sentiment = "中性"
                            
                            latest_news = [{
                                "title": n.get('title'),
                                "url": n.get('url'),
                                "source": n.get('source', 'Google News')
                            } for n in google_news_items[:2]]
                
                except Exception as news_error:
                    logger.warning(f"News fetch failed for {symbol}: {str(news_error)}")
                
                result = {
                    "symbol": symbol,
                    "name": stock_name,
                    "price": current_price,
                    "change": quote.get('change', 0),
                    "change_percent": change_percent,
                    "volume": volume,
                    "market_cap": market_cap / 100000000 if market_cap else 0,
                    "ai_score": min(100, max(0, score)),
                    "reasons": reasons[:3],
                    "recommendation": "買入" if score >= 70 else "觀望" if score >= 50 else "賣出"
                }
                
                # 只在有新聞時才添加新聞欄位
                if news_sentiment:
                    result["news_sentiment"] = news_sentiment
                if latest_news:
                    result["latest_news"] = latest_news
                
                return result
                
            except Exception as e:
                logger.error(f"Quick analyze error {symbol}: {str(e)}")
                return None
        
        # 全部併發執行（小數量可以一次性併發）
        results = await asyncio.gather(
            *[quick_analyze(s) for s in candidate_symbols], 
            return_exceptions=True
        )
        ai_picks = [r for r in results if r and not isinstance(r, Exception)]
        
        # 按 AI 評分排序
        ai_picks.sort(key=lambda x: x['ai_score'], reverse=True)
        
        logger.info(f"✅ AI 推薦完成: 推薦 {len(ai_picks)} 檔")
        
        return {
            "total": len(ai_picks[:limit]),
            "stocks": ai_picks[:limit],
            "note": "AI 評分基於價格動態、基本面分析和新聞情緒"
        }
        
    except Exception as e:
        logger.error(f"AI picks error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI picks: {str(e)}"
        )
