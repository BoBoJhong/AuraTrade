from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio
from apps.core.database import get_db
from apps.core.dependencies import get_current_user
from apps.models.user import User
from apps.core.services.yahoo_finance import YahooFinanceService
from apps.core.services.alpha_vantage_service import alpha_vantage_service, ALPHA_VANTAGE_AVAILABLE
from apps.core.services.twse_service import TWSEService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class RecommendationEngine:
    """AI 股票推薦引擎"""
    
    @staticmethod
    def _calculate_technical_score(indicators: dict) -> tuple[float, list[str]]:
        """
        基於技術指標計算評分 (0-10)
        """
        score = 5.0  # 基礎分
        reasons = []
        
        # RSI 評分
        if indicators.get('rsi'):
            rsi = indicators['rsi'][-1] if isinstance(indicators['rsi'], list) else indicators['rsi']
            if rsi and rsi < 30:
                score += 1.5
                reasons.append('RSI 超賣')
            elif rsi and rsi > 70:
                score -= 1.5
                reasons.append('RSI 超買')
        
        # MACD 評分
        if indicators.get('macd'):
            macd_data = indicators['macd']
            if isinstance(macd_data, dict):
                macd = macd_data.get('macd', [])
                signal = macd_data.get('signal', [])
                if macd and signal and len(macd) > 0 and len(signal) > 0:
                    if macd[-1] > signal[-1]:
                        score += 1.0
                        reasons.append('MACD 金叉')
                    else:
                        score -= 0.5
        
        # MA 評分
        if indicators.get('ma'):
            ma_data = indicators['ma']
            if isinstance(ma_data, dict):
                ma5 = ma_data.get('ma5', [])
                ma20 = ma_data.get('ma20', [])
                if ma5 and ma20 and len(ma5) > 0 and len(ma20) > 0:
                    if ma5[-1] and ma20[-1] and ma5[-1] > ma20[-1]:
                        score += 0.5
                        reasons.append('MA5 > MA20')
        
        return min(10.0, max(0.0, score)), reasons
    
    @staticmethod
    def _calculate_fundamental_score(fundamental: dict) -> tuple[float, list[str]]:
        """
        基於基本面計算評分 (0-10)
        """
        score = 5.0
        reasons = []
        
        # 本益比評分
        pe_ratio = fundamental.get('pe_ratio')
        if pe_ratio and pe_ratio > 0:
            if pe_ratio < 15:
                score += 1.5
                reasons.append(f'低本益比 ({pe_ratio:.2f})')
            elif pe_ratio > 30:
                score -= 1.0
        
        # 殖利率評分
        dividend_yield = fundamental.get('dividend_yield')
        if dividend_yield and dividend_yield > 0:
            if dividend_yield > 5.0:
                score += 1.0
                reasons.append(f'高殖利率 ({dividend_yield:.2f}%)')
            elif dividend_yield > 3.0:
                score += 0.5
        
        # 股價淨值比評分
        pb_ratio = fundamental.get('pb_ratio')
        if pb_ratio and pb_ratio > 0:
            if pb_ratio < 1.5:
                score += 0.5
                reasons.append(f'低股價淨值比 ({pb_ratio:.2f})')
        
        return min(10.0, max(0.0, score)), reasons
    
    @staticmethod
    async def _calculate_sentiment_score(symbol: str) -> tuple[float, list[str]]:
        """
        基於 Alpha Vantage 新聞情緒計算評分 (0-10)
        """
        if not ALPHA_VANTAGE_AVAILABLE:
            return 5.0, []
        
        try:
            # 移除台股後綴 .TW/.TWO
            clean_symbol = symbol.replace('.TW', '').replace('.TWO', '')
            
            sentiment_data = alpha_vantage_service.get_news_sentiment(
                tickers=clean_symbol,
                limit=20
            )
            
            if not sentiment_data or 'feed' not in sentiment_data:
                return 5.0, []
            
            articles = sentiment_data['feed']
            if not articles:
                return 5.0, []
            
            # 計算平均情緒分數
            sentiment_scores = []
            for article in articles[:10]:  # 只取前10篇
                if 'ticker_sentiment' in article:
                    for ticker_sent in article['ticker_sentiment']:
                        if ticker_sent.get('ticker') == clean_symbol:
                            score = float(ticker_sent.get('ticker_sentiment_score', 0))
                            sentiment_scores.append(score)
            
            if not sentiment_scores:
                return 5.0, []
            
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            
            # 轉換為 0-10 分數 (Alpha Vantage sentiment: -1 to 1)
            normalized_score = (avg_sentiment + 1) * 5  # -1~1 -> 0~10
            
            reasons = []
            if avg_sentiment > 0.15:
                reasons.append('新聞情緒極度樂觀')
            elif avg_sentiment > 0.05:
                reasons.append('新聞情緒樂觀')
            elif avg_sentiment < -0.15:
                reasons.append('新聞情緒悲觀')
            
            return normalized_score, reasons
            
        except Exception as e:
            logger.error(f"Sentiment analysis error for {symbol}: {e}")
            return 5.0, []
    
    @staticmethod
    async def generate_recommendations(
        symbols: List[str],
        market: Optional[str] = None
    ) -> List[dict]:
        """
        生成股票推薦列表
        
        Args:
            symbols: 股票代碼列表
            market: 市場篩選 ('TW' or 'US')
        
        Returns:
            [
                {
                    'symbol': '2330.TW',
                    'name': '台積電',
                    'price': 620.0,
                    'change_percent': 1.5,
                    'score': 8.5,
                    'reasons': ['技術面強勢', '基本面穩健'],
                    'market': 'TW'
                },
                ...
            ]
        """
        recommendations = []
        
        for symbol in symbols:
            try:
                # 並行獲取數據
                tasks = [
                    YahooFinanceService.get_stock_info(symbol),
                    YahooFinanceService.get_historical_data(
                        symbol=symbol,
                        period='1mo',
                        interval='1d',
                        db=None
                    )
                ]
                
                # 只有台股才獲取基本面
                if '.TW' in symbol or '.TWO' in symbol:
                    tasks.append(asyncio.to_thread(
                        TWSEService.get_fundamental_data,
                        symbol
                    ))
                else:
                    tasks.append(asyncio.sleep(0))  # placeholder
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                stock_info = results[0] if not isinstance(results[0], Exception) else None
                hist_data = results[1] if not isinstance(results[1], Exception) else None
                fundamental = results[2] if len(results) > 2 and not isinstance(results[2], Exception) else None
                
                if not stock_info:
                    continue
                
                # 計算技術指標分數
                indicators = {}
                if hist_data and len(hist_data) > 0:
                    # 簡單 RSI 計算
                    closes = [d['close'] for d in hist_data if 'close' in d]
                    if len(closes) >= 14:
                        gains = []
                        losses = []
                        for i in range(1, len(closes)):
                            change = closes[i] - closes[i-1]
                            gains.append(max(0, change))
                            losses.append(max(0, -change))
                        
                        avg_gain = sum(gains[-14:]) / 14
                        avg_loss = sum(losses[-14:]) / 14
                        rs = avg_gain / avg_loss if avg_loss > 0 else 0
                        rsi = 100 - (100 / (1 + rs)) if avg_loss > 0 else 100
                        indicators['rsi'] = rsi
                
                technical_score, tech_reasons = RecommendationEngine._calculate_technical_score(indicators)
                
                # 計算基本面分數
                fundamental_score = 5.0
                fund_reasons = []
                if fundamental:
                    fundamental_score, fund_reasons = RecommendationEngine._calculate_fundamental_score(fundamental)
                
                # 計算新聞情緒分數 (只適用於美股)
                sentiment_score = 5.0
                sent_reasons = []
                if 'TW' not in symbol and 'TWO' not in symbol:
                    sentiment_score, sent_reasons = await RecommendationEngine._calculate_sentiment_score(symbol)
                
                # 綜合評分 (加權平均)
                total_score = (
                    technical_score * 0.4 +  # 技術面 40%
                    fundamental_score * 0.4 +  # 基本面 40%
                    sentiment_score * 0.2  # 情緒面 20%
                )
                
                # 合併推薦理由
                all_reasons = tech_reasons + fund_reasons + sent_reasons
                
                recommendations.append({
                    'symbol': symbol,
                    'name': stock_info.get('name', symbol),
                    'price': stock_info.get('price', 0),
                    'change_percent': stock_info.get('change_percent', 0),
                    'score': round(total_score, 1),
                    'reasons': all_reasons[:5],  # 最多5個理由
                    'market': stock_info.get('market', 'US')
                })
                
            except Exception as e:
                logger.error(f"Error generating recommendation for {symbol}: {e}")
                continue
        
        # 按評分排序
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations


@router.get("/recommendations")
async def get_recommendations(
    market: Optional[str] = Query(None, description="Market filter: 'TW' or 'US'"),
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations"),
    current_user: User = Depends(get_current_user)
):
    """
    獲取 AI 推薦股票
    
    - **market**: 市場篩選 ('TW' 或 'US')
    - **limit**: 返回數量 (1-50)
    
    Returns:
        [
            {
                "symbol": "2330.TW",
                "name": "台積電",
                "price": 620.0,
                "change_percent": 1.5,
                "score": 8.5,
                "reasons": ["RSI 超賣", "低本益比"],
                "market": "TW"
            },
            ...
        ]
    """
    try:
        # 建立候選股票池
        candidate_symbols = []
        
        if not market or market == 'TW':
            # 台股熱門股票
            tw_symbols = [
                '2330.TW',  # 台積電
                '2317.TW',  # 鴻海
                '2454.TW',  # 聯發科
                '2881.TW',  # 富邦金
                '2882.TW',  # 國泰金
                '2412.TW',  # 中華電
                '2308.TW',  # 台達電
                '3008.TW',  # 大立光
                '2303.TW',  # 聯電
                '2301.TW',  # 光寶科
                '6505.TW',  # 台塑
                '2382.TW',  # 廣達
                '2603.TW',  # 長榮
                '1301.TW',  # 台塑
                '1303.TW',  # 南亞
            ]
            candidate_symbols.extend(tw_symbols)
        
        if not market or market == 'US':
            # 美股熱門股票
            us_symbols = [
                'AAPL',   # Apple
                'MSFT',   # Microsoft
                'GOOGL',  # Google
                'AMZN',   # Amazon
                'NVDA',   # NVIDIA
                'TSLA',   # Tesla
                'META',   # Meta
                'BRK.B',  # Berkshire Hathaway
                'JPM',    # JPMorgan
                'V',      # Visa
                'JNJ',    # Johnson & Johnson
                'WMT',    # Walmart
                'PG',     # Procter & Gamble
                'MA',     # Mastercard
                'UNH',    # UnitedHealth
            ]
            candidate_symbols.extend(us_symbols)
        
        # 生成推薦
        recommendations = await RecommendationEngine.generate_recommendations(
            symbols=candidate_symbols,
            market=market
        )
        
        # 只返回前 N 個
        return recommendations[:limit]
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
