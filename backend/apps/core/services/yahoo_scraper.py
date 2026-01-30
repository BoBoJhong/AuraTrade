# Yahoo Finance Web Scraper Fallback
# 當 yfinance API 失敗時，直接從網頁爬取數據

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class YahooFinanceScraper:
    '''Yahoo Finance 網頁爬蟲備援'''
    
    BASE_URL = 'https://finance.yahoo.com/quote'
    
    @staticmethod
    def scrape_historical_data(symbol: str, period: str = '1mo'):
        '''
        從 Yahoo Finance 網頁爬取歷史數據
        備援方案：當 yfinance API 失敗時使用
        '''
        try:
            # 計算時間範圍
            end_date = datetime.now()
            if period == '1d':
                start_date = end_date - timedelta(days=1)
            elif period == '5d':
                start_date = end_date - timedelta(days=5)
            elif period == '1mo':
                start_date = end_date - timedelta(days=30)
            elif period == '3mo':
                start_date = end_date - timedelta(days=90)
            elif period == '1y':
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)
            
            # 轉換為 Unix timestamp
            period1 = int(start_date.timestamp())
            period2 = int(end_date.timestamp())
            
            # 構建下載 URL（CSV 格式）
            url = f'https://query1.finance.yahoo.com/v7/finance/download/{symbol}'
            params = {
                'period1': period1,
                'period2': period2,
                'interval': '1d',
                'events': 'history',
                'includeAdjustedClose': 'true'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 解析 CSV 數據
            lines = response.text.strip().split('\n')
            if len(lines) < 2:
                return None
            
            headers_line = lines[0].split(',')
            data = []
            
            for line in lines[1:]:
                values = line.split(',')
                if len(values) >= 6:
                    try:
                        data.append({
                            'date': values[0],
                            'open': float(values[1]),
                            'high': float(values[2]),
                            'low': float(values[3]),
                            'close': float(values[4]),
                            'volume': int(float(values[6])) if len(values) > 6 else 0
                        })
                    except (ValueError, IndexError):
                        continue
            
            logger.info(f'Scraped {len(data)} records for {symbol} from Yahoo Finance web')
            return data if data else None
            
        except Exception as e:
            logger.error(f'Failed to scrape {symbol}: {str(e)}')
            return None
