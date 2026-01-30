"""
FinMind API Service
台灣金融數據平台 - 專注台股的開源數據平台
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class FinMindService:
    """FinMind 金融數據服務"""
    
    BASE_URL = "https://api.finmindtrade.com/api/v4"
    
    @staticmethod
    def get_historical_data(symbol: str, start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """
        獲取歷史股價數據
        
        Args:
            symbol: 股票代碼（不含後綴，例如 "2330"）
            start_date: 開始日期 YYYY-MM-DD
            end_date: 結束日期 YYYY-MM-DD
        
        Returns:
            歷史數據列表
        """
        try:
            stock_code = symbol.replace('.TW', '').replace('.TWO', '')
            
            url = f"{FinMindService.BASE_URL}/data"
            params = {
                'dataset': 'TaiwanStockPrice',
                'data_id': stock_code,
                'start_date': start_date.replace('-', ''),
                'end_date': end_date.replace('-', '')
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('status') == 200 and 'data' in result:
                data = []
                for row in result['data']:
                    # FinMind 格式: {date, stock_id, Trading_Volume, Trading_money, open, max, min, close, ...}
                    try:
                        data.append({
                            'date': row['date'] + 'T00:00:00',
                            'open': float(row['open']),
                            'high': float(row['max']),
                            'low': float(row['min']),
                            'close': float(row['close']),
                            'volume': int(row['Trading_Volume'])
                        })
                    except (KeyError, ValueError) as e:
                        logger.warning(f"Failed to parse FinMind row: {row}, error: {e}")
                        continue
                
                if data:
                    logger.info(f" FinMind API success: {len(data)} records for {symbol}")
                    return data
            return None
            
        except Exception as e:
            logger.error(f" FinMind API failed for {symbol}: {str(e)}")
            return None
    
    @staticmethod
    def get_stock_info(symbol: str) -> Optional[Dict[str, Any]]:
        """
        獲取股票基本資訊
        
        Args:
            symbol: 股票代碼
        
        Returns:
            股票資訊字典
        """
        try:
            stock_code = symbol.replace('.TW', '').replace('.TWO', '')
            
            # 獲取最新價格
            url = f"{FinMindService.BASE_URL}/data"
            today = datetime.now().strftime('%Y-%m-%d')
            yesterday = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
            
            params = {
                'dataset': 'TaiwanStockPrice',
                'data_id': stock_code,
                'start_date': yesterday.replace('-', ''),
                'end_date': today.replace('-', '')
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('status') == 200 and 'data' in result and result['data']:
                latest = result['data'][-1]
                prev = result['data'][-2] if len(result['data']) > 1 else latest
                
                current_price = float(latest['close'])
                prev_price = float(prev['close'])
                change = current_price - prev_price
                
                return {
                    'symbol': symbol,
                    'name': latest.get('stock_id', stock_code),
                    'price': current_price,
                    'change': change,
                    'change_percent': (change / prev_price * 100) if prev_price else 0,
                    'open': float(latest['open']),
                    'high': float(latest['max']),
                    'low': float(latest['min']),
                    'volume': int(latest['Trading_Volume']),
                    'market': 'TW'
                }
            return None
            
        except Exception as e:
            logger.error(f" FinMind stock info failed for {symbol}: {str(e)}")
            return None
