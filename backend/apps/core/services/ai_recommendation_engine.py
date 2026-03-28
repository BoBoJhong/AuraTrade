"""
增強版 AI 股票推薦引擎
支援動態候選池、進階技術指標、深度基本面分析
"""
import asyncio
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
import numpy as np

from apps.core.services.yahoo_finance import YahooFinanceService
from apps.core.services.alpha_vantage_service import alpha_vantage_service, ALPHA_VANTAGE_AVAILABLE
from apps.core.services.twse_service import TWSEService
from apps.core.services.google_news_service import GoogleNewsService
from apps.models.ai_recommendation import AIRecommendation

logger = logging.getLogger(__name__)


class EnhancedAIRecommendationEngine:
    """增強版 AI 推薦引擎"""
    
    # 台股市值前 50（簡化版，實際可從資料庫或 API 動態取得）
    TOP_TW_STOCKS = [
        "2330.TW", "2317.TW", "2454.TW", "2412.TW", "2308.TW",
        "2882.TW", "2881.TW", "2303.TW", "2891.TW", "2886.TW",
        "2002.TW", "1301.TW", "2207.TW", "3711.TW", "2382.TW",
        "2912.TW", "1216.TW", "2357.TW", "3008.TW", "2395.TW",
        "2301.TW", "2327.TW", "2884.TW", "2892.TW", "1303.TW",
        "2409.TW", "2408.TW", "2885.TW", "5880.TW", "2887.TW",
        "0050.TW", "006208.TW", "0056.TW", "00878.TW", "00881.TW",
        "2603.TW", "2615.TW", "4938.TW", "2383.TW", "3045.TW",
        "2379.TW", "2356.TW", "2474.TW", "6505.TW", "3034.TW",
        "2609.TW", "2324.TW", "2353.TW", "2201.TW", "2377.TW"
    ]
    
    # 美股市值前 50（簡化版）
    TOP_US_STOCKS = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
        "META", "TSLA", "BRK.B", "TSM", "V",
        "UNH", "XOM", "JNJ", "WMT", "JPM",
        "MA", "PG", "LLY", "HD", "CVX",
        "MRK", "ABBV", "KO", "AVGO", "PEP",
        "COST", "ADBE", "TMO", "MCD", "ACN",
        "CSCO", "ABT", "NKE", "CRM", "DHR",
        "VZ", "ORCL", "TXN", "CMCSA", "DIS",
        "INTC", "AMD", "QCOM", "NFLX", "PFE",
        "PM", "UPS", "RTX", "NEE", "HON"
    ]
    
    @staticmethod
    def _calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: int = 2) -> Dict:
        """計算布林通道"""
        if len(prices) < period:
            return {}
        
        prices_array = np.array(prices[-period:])
        sma = np.mean(prices_array)
        std = np.std(prices_array)
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        current_price = prices[-1]
        
        # 計算價格在通道中的位置 (0-1)
        bb_position = (current_price - lower_band) / (upper_band - lower_band) if upper_band != lower_band else 0.5
        
        return {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band,
            'position': bb_position,
            'width': (upper_band - lower_band) / sma if sma > 0 else 0
        }
    
    @staticmethod
    def _calculate_kd(highs: List[float], lows: List[float], closes: List[float], period: int = 9) -> Dict:
        """計算 KD 指標"""
        if len(highs) < period or len(lows) < period or len(closes) < period:
            return {}
        
        # RSV (Raw Stochastic Value)
        rsv_values = []
        for i in range(period - 1, len(closes)):
            period_high = max(highs[i - period + 1:i + 1])
            period_low = min(lows[i - period + 1:i + 1])
            close = closes[i]
            
            if period_high != period_low:
                rsv = ((close - period_low) / (period_high - period_low)) * 100
            else:
                rsv = 50
            rsv_values.append(rsv)
        
        # K值 = 前一日K值 × 2/3 + 當日RSV × 1/3
        k_values = [50]  # 初始值
        for rsv in rsv_values:
            k = (k_values[-1] * 2 / 3) + (rsv * 1 / 3)
            k_values.append(k)
        
        # D值 = 前一日D值 × 2/3 + 當日K值 × 1/3
        d_values = [50]  # 初始值
        for k in k_values[1:]:
            d = (d_values[-1] * 2 / 3) + (k * 1 / 3)
            d_values.append(d)
        
        return {
            'k': k_values[-1],
            'd': d_values[-1],
            'j': 3 * k_values[-1] - 2 * d_values[-1]  # J = 3K - 2D
        }
    
    @staticmethod
    def _calculate_volume_ratio(volumes: List[float], period: int = 5) -> float:
        """計算量比"""
        if len(volumes) < period + 1:
            return 1.0
        
        current_volume = volumes[-1]
        avg_volume = np.mean(volumes[-period-1:-1])
        
        return current_volume / avg_volume if avg_volume > 0 else 1.0

    @staticmethod
    def _calculate_bias(prices: List[float], period: int = 5) -> Dict:
        """
        計算 BIAS（乖離率）

        公式：
            BIAS = (當日收盤價 - N日移動平均價) / N日移動平均價 * 100
        """
        if len(prices) < period:
            return {}

        ma_n = np.mean(prices[-period:])
        if ma_n == 0:
            return {}

        current_price = prices[-1]
        bias = ((current_price - ma_n) / ma_n) * 100

        if bias < -5:
            zone = "oversold"
        elif bias > 5:
            zone = "overbought"
        else:
            zone = "neutral"

        return {
            'period': period,
            'ma': round(ma_n, 2),
            'bias': round(bias, 2),
            'zone': zone,
        }
    
    @staticmethod
    async def _calculate_advanced_technical_score(
        symbol: str,
        hist_data: List[Dict]
    ) -> Tuple[float, List[str], Dict]:
        """
        進階技術指標評分 (0-100)
        返回: (分數, 理由列表, 技術指標字典)
        """
        score = 50.0
        reasons = []
        indicators = {}
        
        if not hist_data or len(hist_data) < 20:
            return score, reasons, indicators
        
        try:
            closes = [d['close'] for d in hist_data if 'close' in d]
            highs = [d['high'] for d in hist_data if 'high' in d]
            lows = [d['low'] for d in hist_data if 'low' in d]
            volumes = [d['volume'] for d in hist_data if 'volume' in d]
            
            # 1. RSI 指標
            if len(closes) >= 14:
                gains, losses = [], []
                for i in range(1, len(closes)):
                    change = closes[i] - closes[i-1]
                    gains.append(max(0, change))
                    losses.append(max(0, -change))
                
                avg_gain = np.mean(gains[-14:])
                avg_loss = np.mean(losses[-14:])
                rs = avg_gain / avg_loss if avg_loss > 0 else 0
                rsi = 100 - (100 / (1 + rs)) if avg_loss > 0 else 100
                
                indicators['rsi'] = round(rsi, 2)
                
                if 30 < rsi < 40:
                    score += 15
                    reasons.append(f'RSI 接近超賣區 ({rsi:.1f})')
                elif rsi < 30:
                    score += 20
                    reasons.append(f'RSI 超賣 ({rsi:.1f})')
                elif 60 < rsi < 70:
                    score += 5
                    reasons.append(f'RSI 強勢 ({rsi:.1f})')
                elif rsi > 75:
                    score -= 15
                    reasons.append(f'RSI 超買風險 ({rsi:.1f})')
            
            # 2. 布林通道
            bb = EnhancedAIRecommendationEngine._calculate_bollinger_bands(closes)
            if bb:
                indicators['bollinger_bands'] = bb
                bb_pos = bb['position']
                
                if bb_pos < 0.2:
                    score += 15
                    reasons.append('價格接近布林下軌')
                elif bb_pos > 0.8:
                    score -= 10
                    reasons.append('價格接近布林上軌')
                
                if bb['width'] < 0.05:
                    score += 5
                    reasons.append('布林通道收窄，即將突破')
            
            # 3. KD 指標
            if len(highs) >= 9 and len(lows) >= 9:
                kd = EnhancedAIRecommendationEngine._calculate_kd(highs, lows, closes)
                if kd:
                    indicators['kd'] = kd
                    k, d = kd['k'], kd['d']
                    
                    if k < 20 and d < 20:
                        score += 15
                        reasons.append(f'KD 超賣區 (K:{k:.1f}, D:{d:.1f})')
                    elif k > d and k < 50:
                        score += 10
                        reasons.append('KD 低檔金叉')
                    elif k > 80 and d > 80:
                        score -= 10
                        reasons.append(f'KD 超買區 (K:{k:.1f}, D:{d:.1f})')
            
            # 4. 均線系統
            if len(closes) >= 60:
                ma5 = np.mean(closes[-5:])
                ma20 = np.mean(closes[-20:])
                ma60 = np.mean(closes[-60:])
                current = closes[-1]
                
                indicators['ma'] = {
                    'ma5': round(ma5, 2),
                    'ma20': round(ma20, 2),
                    'ma60': round(ma60, 2)
                }
                
                if ma5 > ma20 > ma60:
                    score += 15
                    reasons.append('多頭排列')
                elif ma5 > ma20:
                    score += 8
                    reasons.append('短期多頭')
                elif ma5 < ma20 < ma60:
                    score -= 10
                    reasons.append('空頭排列')
                
                if current > ma5:
                    score += 3

            # 4.1 BIAS (乖離率)
            if len(closes) >= 5:
                bias5 = EnhancedAIRecommendationEngine._calculate_bias(closes, period=5)
                if bias5:
                    indicators['bias_5'] = bias5
                    bias_val = bias5['bias']
                    bias_zone = bias5['zone']

                    if bias_zone == 'oversold':
                        score += 12
                        reasons.append(f"BIAS 超跌 ({bias_val:.1f}%)")
                    elif bias_zone == 'overbought':
                        score -= 10
                        reasons.append(f"BIAS 過熱 ({bias_val:.1f}%)")
                    else:
                        reasons.append(f"BIAS 中性 ({bias_val:.1f}%)")
            
            # 5. 量比分析
            if len(volumes) >= 6:
                vol_ratio = EnhancedAIRecommendationEngine._calculate_volume_ratio(volumes)
                indicators['volume_ratio'] = round(vol_ratio, 2)
                
                if vol_ratio > 2.0:
                    score += 10
                    reasons.append(f'量能爆發 (量比 {vol_ratio:.1f})')
                elif vol_ratio > 1.5:
                    score += 5
                    reasons.append(f'量能放大 (量比 {vol_ratio:.1f})')
                elif vol_ratio < 0.5:
                    score -= 5
                    reasons.append('量能萎縮')
            
            # 6. 趨勢強度
            if len(closes) >= 20:
                price_change_20d = (closes[-1] - closes[-20]) / closes[-20] * 100
                indicators['trend_20d'] = round(price_change_20d, 2)
                
                if price_change_20d > 15:
                    score += 10
                    reasons.append(f'20日強勢上漲 ({price_change_20d:.1f}%)')
                elif price_change_20d > 5:
                    score += 5
                elif price_change_20d < -15:
                    score -= 10
                    reasons.append(f'20日跌幅較大 ({price_change_20d:.1f}%)')
            
        except Exception as e:
            logger.error(f"Technical analysis error for {symbol}: {e}")
        
        return min(100.0, max(0.0, score)), reasons[:6], indicators
    
    @staticmethod
    def _calculate_advanced_fundamental_score(
        fundamental: Dict
    ) -> Tuple[float, List[str], Dict]:
        """
        深度基本面評分 (0-100)
        返回: (分數, 理由列表, 基本面數據字典)
        """
        score = 50.0
        reasons = []
        fund_data = {}
        
        if not fundamental:
            return score, reasons, fund_data
        
        try:
            # 1. 本益比 (PE Ratio)
            pe = fundamental.get('pe_ratio')
            if pe and pe > 0:
                fund_data['pe_ratio'] = round(pe, 2)
                if 8 < pe < 15:
                    score += 15
                    reasons.append(f'低本益比 ({pe:.1f})')
                elif 15 <= pe < 25:
                    score += 8
                    reasons.append(f'本益比合理 ({pe:.1f})')
                elif pe > 40:
                    score -= 10
                    reasons.append(f'本益比偏高 ({pe:.1f})')
            
            # 2. 股價淨值比 (PB Ratio)
            pb = fundamental.get('pb_ratio')
            if pb and pb > 0:
                fund_data['pb_ratio'] = round(pb, 2)
                if pb < 1.0:
                    score += 12
                    reasons.append(f'股價低於淨值 (PB:{pb:.2f})')
                elif pb < 1.5:
                    score += 8
                    reasons.append(f'股價淨值比低 (PB:{pb:.2f})')
            
            # 3. 殖利率 (Dividend Yield)
            div_yield = fundamental.get('dividend_yield')
            if div_yield and div_yield > 0:
                fund_data['dividend_yield'] = round(div_yield, 2)
                if div_yield > 6:
                    score += 15
                    reasons.append(f'高殖利率 ({div_yield:.1f}%)')
                elif div_yield > 4:
                    score += 10
                    reasons.append(f'殖利率佳 ({div_yield:.1f}%)')
                elif div_yield > 2:
                    score += 5
            
            # 4. ROE (股東權益報酬率)
            roe = fundamental.get('roe')
            if roe:
                fund_data['roe'] = round(roe, 2)
                if roe > 20:
                    score += 12
                    reasons.append(f'高ROE ({roe:.1f}%)')
                elif roe > 15:
                    score += 8
                    reasons.append(f'ROE優秀 ({roe:.1f}%)')
                elif roe < 5:
                    score -= 8
                    reasons.append(f'ROE偏低 ({roe:.1f}%)')
            
            # 5. 負債比
            debt_ratio = fundamental.get('debt_ratio')
            if debt_ratio is not None:
                fund_data['debt_ratio'] = round(debt_ratio, 2)
                if debt_ratio < 30:
                    score += 8
                    reasons.append(f'低負債比 ({debt_ratio:.1f}%)')
                elif debt_ratio > 70:
                    score -= 10
                    reasons.append(f'負債比偏高 ({debt_ratio:.1f}%)')
            
            # 6. EPS 成長率
            eps_growth = fundamental.get('eps_growth')
            if eps_growth:
                fund_data['eps_growth'] = round(eps_growth, 2)
                if eps_growth > 20:
                    score += 15
                    reasons.append(f'EPS高成長 ({eps_growth:.1f}%)')
                elif eps_growth > 10:
                    score += 10
                    reasons.append(f'EPS成長 ({eps_growth:.1f}%)')
                elif eps_growth < -10:
                    score -= 12
                    reasons.append(f'EPS衰退 ({eps_growth:.1f}%)')
            
            # 7. 毛利率
            gross_margin = fundamental.get('gross_margin')
            if gross_margin:
                fund_data['gross_margin'] = round(gross_margin, 2)
                if gross_margin > 50:
                    score += 8
                    reasons.append(f'高毛利率 ({gross_margin:.1f}%)')
                elif gross_margin < 20:
                    score -= 5
        
        except Exception as e:
            logger.error(f"Fundamental analysis error: {e}")
        
        return min(100.0, max(0.0, score)), reasons[:5], fund_data
    
    @staticmethod
    async def _calculate_sentiment_score(
        symbol: str,
        stock_name: str
    ) -> Tuple[float, List[str], str, List[Dict]]:
        """
        新聞情緒評分 (0-100)
        返回: (分數, 理由列表, 情緒標籤, 最新新聞)
        """
        score = 50.0
        reasons = []
        sentiment_label = "中性"
        latest_news = []
        
        try:
            google_news = GoogleNewsService()
            
            # 美股優先用 Alpha Vantage
            if not symbol.endswith('.TW') and not symbol.endswith('.TWO') and ALPHA_VANTAGE_AVAILABLE:
                try:
                    av_news = await alpha_vantage_service.get_news_sentiment(tickers=symbol, limit=5)
                    if av_news and 'feed' in av_news:
                        articles = av_news['feed']
                        if articles:
                            sentiment_scores = [a.get('overall_sentiment_score', 0) for a in articles]
                            avg_sentiment = np.mean(sentiment_scores)
                            
                            if avg_sentiment > 0.25:
                                score += 20
                                reasons.append('新聞情緒強烈正面')
                                sentiment_label = "正面"
                            elif avg_sentiment > 0.1:
                                score += 12
                                reasons.append('新聞情緒正面')
                                sentiment_label = "偏正面"
                            elif avg_sentiment < -0.25:
                                score -= 18
                                reasons.append('新聞情緒負面')
                                sentiment_label = "負面"
                            elif avg_sentiment < -0.1:
                                score -= 10
                                reasons.append('新聞情緒偏負面')
                                sentiment_label = "偏負面"
                            
                            latest_news = [{
                                'title': a.get('title'),
                                'url': a.get('url'),
                                'source': a.get('source'),
                                'sentiment': a.get('overall_sentiment_label')
                            } for a in articles[:3]]
                            
                            return min(100.0, max(0.0, score)), reasons, sentiment_label, latest_news
                except Exception as e:
                    logger.warning(f"Alpha Vantage sentiment error: {e}")
            
            # 使用 Google News (台股或美股備援)
            lang = "zh-TW" if symbol.endswith(('.TW', '.TWO')) else "en"
            news_items = await google_news.fetch_stock_news(symbol, stock_name, lang, max_results=5)
            
            if news_items:
                positive_keywords = ['增長', '上漲', '突破', '創新高', '買進', 'surge', 'growth', 'bullish', 'rally', 'gain']
                negative_keywords = ['下跌', '虧損', '警告', '風險', '賣出', 'fall', 'drop', 'bearish', 'loss', 'decline']
                
                pos_count = sum(1 for n in news_items if any(k in n.get('title', '').lower() for k in positive_keywords))
                neg_count = sum(1 for n in news_items if any(k in n.get('title', '').lower() for k in negative_keywords))
                
                if pos_count > neg_count and pos_count >= 2:
                    score += 15
                    reasons.append('近期新聞偏正面')
                    sentiment_label = "偏正面"
                elif neg_count > pos_count and neg_count >= 2:
                    score -= 12
                    reasons.append('近期新聞偏負面')
                    sentiment_label = "偏負面"
                
                latest_news = [{
                    'title': n.get('title'),
                    'url': n.get('link'),
                    'source': n.get('source', 'Google News')
                } for n in news_items[:3]]
        
        except Exception as e:
            logger.error(f"Sentiment analysis error for {symbol}: {e}")
        
        return min(100.0, max(0.0, score)), reasons, sentiment_label, latest_news
    
    @staticmethod
    def _calculate_confidence(
        tech_score: float,
        fund_score: float,
        sent_score: float,
        data_completeness: Dict
    ) -> float:
        """
        計算信心度 (0-100)
        基於數據完整性和分數一致性
        """
        confidence = 50.0
        
        # 數據完整性加分
        if data_completeness.get('technical'):
            confidence += 15
        if data_completeness.get('fundamental'):
            confidence += 15
        if data_completeness.get('sentiment'):
            confidence += 10
        
        # 分數一致性加分
        scores = [tech_score, fund_score, sent_score]
        score_std = np.std(scores)
        
        if score_std < 10:  # 分數非常一致
            confidence += 10
        elif score_std < 20:  # 分數較一致
            confidence += 5
        else:  # 分數分歧
            confidence -= 10
        
        return min(100.0, max(0.0, confidence))
    
    @staticmethod
    async def analyze_stock(
        symbol: str,
        db: AsyncSession
    ) -> Optional[Dict]:
        """
        分析單一股票並生成推薦
        """
        try:
            # 獲取股票資訊
            stock_info = await YahooFinanceService.get_stock_info(symbol)
            if not stock_info or not stock_info.get('price'):
                return None
            
            # 獲取歷史數據
            hist_data = await YahooFinanceService.get_historical_data(
                symbol=symbol,
                period='3mo',
                interval='1d',
                db=None
            )
            
            # 獲取基本面數據（台股）
            fundamental = {}
            if symbol.endswith(('.TW', '.TWO')):
                try:
                    fundamental = await asyncio.to_thread(
                        TWSEService.get_fundamental_data,
                        symbol
                    )
                except Exception as e:
                    logger.warning(f"Failed to get fundamental for {symbol}: {e}")
            
            # 進階技術分析
            tech_score, tech_reasons, tech_indicators = await EnhancedAIRecommendationEngine._calculate_advanced_technical_score(
                symbol, hist_data
            )
            
            # 深度基本面分析
            fund_score, fund_reasons, fund_data = EnhancedAIRecommendationEngine._calculate_advanced_fundamental_score(
                fundamental
            )
            
            # 新聞情緒分析
            sent_score, sent_reasons, sentiment_label, latest_news = await EnhancedAIRecommendationEngine._calculate_sentiment_score(
                symbol, stock_info.get('name', symbol)
            )
            
            # 綜合評分 (加權平均)
            ai_score = (
                tech_score * 0.45 +      # 技術面 45%
                fund_score * 0.35 +      # 基本面 35%
                sent_score * 0.20        # 情緒面 20%
            )
            
            # 數據完整性
            data_completeness = {
                'technical': bool(tech_indicators),
                'fundamental': bool(fund_data),
                'sentiment': bool(latest_news)
            }
            
            # 計算信心度
            confidence = EnhancedAIRecommendationEngine._calculate_confidence(
                tech_score, fund_score, sent_score, data_completeness
            )
            
            # 決定推薦
            if ai_score >= 70:
                recommendation = "買入"
            elif ai_score >= 50:
                recommendation = "觀望"
            else:
                recommendation = "賣出"
            
            # 合併理由
            all_reasons = tech_reasons + fund_reasons + sent_reasons
            
            result = {
                'symbol': symbol,
                'stock_name': stock_info.get('name', symbol),
                'market': 'TW' if symbol.endswith(('.TW', '.TWO')) else 'US',
                'price': stock_info.get('price'),
                'change_percent': stock_info.get('change_percent', 0),
                'ai_score': round(ai_score, 1),
                'recommendation': recommendation,
                'confidence': round(confidence, 1),
                'technical_score': round(tech_score, 1),
                'fundamental_score': round(fund_score, 1),
                'sentiment_score': round(sent_score, 1),
                'reasons': all_reasons[:8],  # 最多8個理由
                'technical_indicators': tech_indicators,
                'fundamental_data': fund_data,
                'news_sentiment': sentiment_label,
                'latest_news': latest_news,
                'bias_5': tech_indicators.get('bias_5', {}).get('bias'),
                'bias_zone': tech_indicators.get('bias_5', {}).get('zone'),
                'recommended_at': datetime.utcnow()
            }
            
            # 儲存到資料庫
            try:
                ai_rec = AIRecommendation(**result)
                db.add(ai_rec)
                await db.commit()
                logger.info(f"✅ Saved AI recommendation for {symbol}: {recommendation} (score: {ai_score:.1f})")
            except Exception as e:
                logger.error(f"Failed to save AI recommendation for {symbol}: {e}")
                await db.rollback()
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    @staticmethod
    async def generate_recommendations(
        db: AsyncSession,
        market: Optional[str] = None,
        limit: int = 10,
        min_score: float = 60.0,
        max_candidates: int = 20  # 新增：限制最大候選數
    ) -> List[Dict]:
        """
        生成 AI 推薦清單
        
        Args:
            db: 資料庫會話
            market: 市場篩選 ('TW' or 'US')
            limit: 返回數量
            min_score: 最低評分門檻
            max_candidates: 最大候選數量（優化效能）
        """
        # 動態候選池（優化效能：減少掃描數量）
        candidate_symbols = []
        
        if market == 'TW':
            # 只掃描台股
            candidate_symbols.extend(EnhancedAIRecommendationEngine.TOP_TW_STOCKS[:max_candidates])
        elif market == 'US':
            # 只掃描美股
            candidate_symbols.extend(EnhancedAIRecommendationEngine.TOP_US_STOCKS[:max_candidates])
        else:
            # 全市場：各取一半
            tw_count = max_candidates // 2
            us_count = max_candidates - tw_count
            candidate_symbols.extend(EnhancedAIRecommendationEngine.TOP_TW_STOCKS[:tw_count])
            candidate_symbols.extend(EnhancedAIRecommendationEngine.TOP_US_STOCKS[:us_count])
        
        logger.info(f"🔍 AI掃描: {len(candidate_symbols)} 檔候選股票 (市場: {market or '全部'})")
        
        # 分批並行分析（避免過多併發和 API 限流）
        batch_size = 3  # 減少到每批 3 支，更保守避免限流
        all_results = []
        
        for i in range(0, len(candidate_symbols), batch_size):
            batch = candidate_symbols[i:i + batch_size]
            logger.info(f"  處理批次 {i//batch_size + 1}/{(len(candidate_symbols) + batch_size - 1)//batch_size}: {batch}")
            
            tasks = [
                EnhancedAIRecommendationEngine.analyze_stock(symbol, db)
                for symbol in batch
            ]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            all_results.extend(batch_results)
            
            # 批次間延遲增加到 2 秒，避免 Yahoo Finance 限流
            if i + batch_size < len(candidate_symbols):
                await asyncio.sleep(2.0)
        
        results = all_results
        
        # 過濾有效結果
        recommendations = [
            r for r in results
            if r and not isinstance(r, Exception) and r.get('ai_score', 0) >= min_score
        ]
        
        # 按 AI 評分排序
        recommendations.sort(key=lambda x: x['ai_score'], reverse=True)
        
        logger.info(f"✅ AI推薦完成: {len(recommendations)} 檔符合條件 (≥{min_score}分)")
        
        return recommendations[:limit]
    
    @staticmethod
    async def get_recommendation_statistics(db: AsyncSession, days: int = 30) -> Dict:
        """
        獲取推薦統計數據（用於未來回測）
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            stmt = select(
                func.count(AIRecommendation.id).label('total'),
                func.avg(AIRecommendation.ai_score).label('avg_score'),
                func.count(AIRecommendation.id).filter(AIRecommendation.recommendation == '買入').label('buy_count'),
                func.count(AIRecommendation.id).filter(AIRecommendation.recommendation == '觀望').label('hold_count'),
                func.count(AIRecommendation.id).filter(AIRecommendation.recommendation == '賣出').label('sell_count'),
            ).where(
                AIRecommendation.recommended_at >= cutoff_date
            )
            
            result = await db.execute(stmt)
            row = result.first()
            
            return {
                'total_recommendations': row.total or 0,
                'average_score': round(row.avg_score, 2) if row.avg_score else 0,
                'buy_count': row.buy_count or 0,
                'hold_count': row.hold_count or 0,
                'sell_count': row.sell_count or 0,
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Error getting recommendation statistics: {e}")
            return {}
