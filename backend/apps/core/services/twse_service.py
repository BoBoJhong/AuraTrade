"""
TWSE (Taiwan Stock Exchange) API Service
台灣證券交易所官方 API - 最穩定的台股數據源
升級版：整合 TWSE OpenAPI v1 (openapi.twse.com.tw/v1)
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TWSEService:
    """台灣證交所官方 API 服務"""
    
    BASE_URL = "https://www.twse.com.tw/rwd/zh"
    OPENAPI_BASE_URL = "https://openapi.twse.com.tw/v1"
    
    @staticmethod
    def get_historical_data(symbol: str, start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """
        獲取歷史股價數據
        
        Args:
            symbol: 股票代碼（不含 .TW 後綴，例如 "2330"）
            start_date: 開始日期 YYYYMMDD
            end_date: 結束日期 YYYYMMDD
        
        Returns:
            歷史數據列表 [{date, open, high, low, close, volume}, ...]
        """
        try:
            # 移除 .TW 或 .TWO 後綴
            stock_code = symbol.replace('.TW', '').replace('.TWO', '')
            
            # TWSE API 參數
            url = f"{TWSEService.BASE_URL}/afterTrading/STOCK_DAY"
            
            # 按月份獲取數據
            data = []
            current = datetime.strptime(start_date, '%Y%m%d')
            end = datetime.strptime(end_date, '%Y%m%d')
            
            while current <= end:
                params = {
                    'date': current.strftime('%Y%m%d'),
                    'stockNo': stock_code,
                    'response': 'json'
                }
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                
                result = response.json()
                
                # 解析數據
                if result.get('stat') == 'OK' and 'data' in result:
                    for row in result['data']:
                        # TWSE 格式: ["109/12/01","10,123","10,456","10,089","10,234","12345678"]
                        # 日期/開盤/最高/最低/收盤/成交量
                        try:
                            date_str = row[0].replace('/', '-')  # ROC date to ISO
                            # Convert ROC year (民國) to AD year (西元)
                            year, month, day = date_str.split('-')
                            year = str(int(year) + 1911)
                            date_iso = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                            
                            data.append({
                                'date': f"{date_iso}T00:00:00",
                                'open': float(row[3].replace(',', '')),
                                'high': float(row[4].replace(',', '')),
                                'low': float(row[5].replace(',', '')),
                                'close': float(row[6].replace(',', '')),
                                'volume': int(row[1].replace(',', ''))
                            })
                        except (ValueError, IndexError) as e:
                            logger.warning(f"Failed to parse TWSE row: {row}, error: {e}")
                            continue
                
                # 移到下個月
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)
            
            if data:
                logger.info(f" TWSE API success: {len(data)} records for {symbol}")
                return data
            return None
            
        except Exception as e:
            logger.error(f" TWSE API failed for {symbol}: {str(e)}")
            return None
    
    @staticmethod
    def get_stock_info(symbol: str) -> Optional[Dict[str, Any]]:
        """
        獲取即時股價資訊
        
        Args:
            symbol: 股票代碼（不含後綴）
        
        Returns:
            股票資訊字典
        """
        try:
            stock_code = symbol.replace('.TW', '').replace('.TWO', '')
            
            url = f"{TWSEService.BASE_URL}/afterTrading/MI_INDEX"
            params = {
                'date': datetime.now().strftime('%Y%m%d'),
                'type': 'ALLBUT0999',
                'response': 'json'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('stat') == 'OK' and 'data9' in result:
                for row in result['data9']:
                    if row[0] == stock_code:
                        # [代碼, 名稱, 成交量, 成交金額, 開盤, 最高, 最低, 收盤, 漲跌, ...]
                        return {
                            'symbol': symbol,
                            'name': row[1],
                            'price': float(row[8].replace(',', '')),
                            'change': float(row[9].replace(',', '')),
                            'open': float(row[5].replace(',', '')),
                            'high': float(row[6].replace(',', '')),
                            'low': float(row[7].replace(',', '')),
                            'volume': int(row[2].replace(',', '')),
                            'market': 'TW'
                        }
            return None
            
        except Exception as e:
            logger.error(f" TWSE stock info failed for {symbol}: {str(e)}")
            return None    
    @staticmethod
    def get_fundamental_data(symbol: str) -> Optional[Dict[str, Any]]:
        """
        獲取基本面數據（本益比、殖利率、股價淨值比）
        使用 TWSE OpenAPI: /exchangeReport/BWIBBU_ALL
        
        Args:
            symbol: 股票代碼（不含後綴）
        
        Returns:
            {
                'symbol': '2330',
                'name': '台積電',
                'pe_ratio': 25.5,  # 本益比
                'dividend_yield': 2.3,  # 殖利率 (%)
                'pb_ratio': 5.2  # 股價淨值比
            }
        """
        try:
            stock_code = symbol.replace('.TW', '').replace('.TWO', '')
            
            url = f"{TWSEService.OPENAPI_BASE_URL}/exchangeReport/BWIBBU_ALL"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # 搜尋特定股票代碼
            for row in data:
                if row.get('Code') == stock_code:
                    return {
                        'symbol': stock_code,
                        'name': row.get('Name', ''),
                        'pe_ratio': float(row.get('PEratio', 0)) if row.get('PEratio') != '-' else None,
                        'dividend_yield': float(row.get('DividendYield', 0)) if row.get('DividendYield') != '-' else None,
                        'pb_ratio': float(row.get('PBratio', 0)) if row.get('PBratio') != '-' else None
                    }
            
            logger.warning(f"Stock {stock_code} not found in fundamental data")
            return None
            
        except Exception as e:
            logger.error(f"TWSE fundamental data failed for {symbol}: {str(e)}")
            return None
    
    @staticmethod
    def get_institutional_investors(date: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """
        獲取三大法人買賣超資訊
        使用 TWSE OpenAPI: /fund/MI_QFIIS (簡化版，單日資料)
        
        Args:
            date: 查詢日期 YYYYMMDD，預設為今天
        
        Returns:
            [{
                'symbol': '2330',
                'name': '台積電',
                'foreign_buy': 1000,  # 外資買進（千股）
                'foreign_sell': 800,
                'foreign_net': 200,  # 外資買賣超
                'trust_net': 50,  # 投信買賣超
                'dealer_net': -30  # 自營商買賣超
            }, ...]
        """
        try:
            if date is None:
                date = datetime.now().strftime('%Y%m%d')
            
            # 注意：實際 API 可能需要不同格式，這裡先用範例格式
            url = f"{TWSEService.OPENAPI_BASE_URL}/fund/MI_QFIIS"
            params = {'date': date}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # 解析法人資料（實際格式需根據 API 回應調整）
            result = []
            # TODO: 根據實際 API 回應格式解析
            logger.info(f"Fetched institutional data for {date}")
            return result
            
        except Exception as e:
            logger.error(f"TWSE institutional data failed: {str(e)}")
            return None
    
    @staticmethod
    def get_dividend_info(symbol: str) -> Optional[Dict[str, Any]]:
        """
        獲取股利資訊
        使用 TWSE OpenAPI: /opendata/t187ap45_L
        
        Args:
            symbol: 股票代碼（不含後綴）
        
        Returns:
            {
                'symbol': '2330',
                'name': '台積電',
                'cash_dividend': 10.0,  # 現金股利
                'stock_dividend': 0.0,  # 股票股利
                'ex_dividend_date': '2025-06-15',  # 除息日
                'total_dividend': 10.0  # 合計股利
            }
        """
        try:
            stock_code = symbol.replace('.TW', '').replace('.TWO', '')
            
            url = f"{TWSEService.OPENAPI_BASE_URL}/opendata/t187ap45_L"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # 搜尋特定股票的最新股利資訊
            for row in data:
                if row.get('公司代號') == stock_code or row.get('Code') == stock_code:
                    return {
                        'symbol': stock_code,
                        'name': row.get('公司名稱', row.get('Name', '')),
                        'cash_dividend': float(row.get('現金股利', row.get('CashDividend', 0))),
                        'stock_dividend': float(row.get('股票股利', row.get('StockDividend', 0))),
                        'ex_dividend_date': row.get('除息日', row.get('ExDividendDate', '')),
                        'total_dividend': float(row.get('合計', row.get('Total', 0)))
                    }
            
            logger.warning(f"Dividend info not found for {stock_code}")
            return None
            
        except Exception as e:
            logger.error(f"TWSE dividend info failed for {symbol}: {str(e)}")
            return None