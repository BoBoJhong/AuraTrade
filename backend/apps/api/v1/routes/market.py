"""
Market Data API Routes
市場資料 API - 基本面分析、法人動態、股利資訊
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from apps.core.services.twse_service import TWSEService
from apps.core.dependencies import get_current_user
from apps.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/fundamental/{symbol}")
async def get_fundamental_data(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """
    獲取股票基本面資料
    
    回傳：
    - pe_ratio: 本益比
    - dividend_yield: 殖利率 (%)
    - pb_ratio: 股價淨值比
    """
    try:
        # 確保股票代碼格式正確
        if not symbol.endswith('.TW') and not symbol.endswith('.TWO'):
            symbol = f"{symbol}.TW"
        
        data = TWSEService.get_fundamental_data(symbol)
        
        if data is None:
            raise HTTPException(
                status_code=404,
                detail=f"無法取得 {symbol} 的基本面資料"
            )
        
        return {
            "success": True,
            "data": data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch fundamental data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"取得基本面資料失敗: {str(e)}"
        )


@router.get("/dividend/{symbol}")
async def get_dividend_info(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """
    獲取股票股利資訊
    
    回傳：
    - cash_dividend: 現金股利
    - stock_dividend: 股票股利
    - ex_dividend_date: 除息日
    - total_dividend: 合計股利
    """
    try:
        # 確保股票代碼格式正確
        if not symbol.endswith('.TW') and not symbol.endswith('.TWO'):
            symbol = f"{symbol}.TW"
        
        data = TWSEService.get_dividend_info(symbol)
        
        if data is None:
            raise HTTPException(
                status_code=404,
                detail=f"無法取得 {symbol} 的股利資訊"
            )
        
        return {
            "success": True,
            "data": data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch dividend info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"取得股利資訊失敗: {str(e)}"
        )


@router.get("/institutional")
async def get_institutional_investors(
    date: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    獲取三大法人買賣超資訊
    
    參數：
    - date: 查詢日期 YYYYMMDD（選填，預設今天）
    
    回傳：
    - 外資、投信、自營商買賣超資料
    """
    try:
        data = TWSEService.get_institutional_investors(date)
        
        if data is None:
            raise HTTPException(
                status_code=404,
                detail="無法取得法人買賣超資料"
            )
        
        return {
            "success": True,
            "data": data,
            "date": date
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch institutional data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"取得法人資料失敗: {str(e)}"
        )


@router.get("/stock-info/{symbol}")
async def get_comprehensive_stock_info(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """
    獲取股票綜合資訊（價格 + 基本面 + 股利）
    
    一次性獲取所有可用資訊，方便前端顯示
    """
    try:
        # 確保股票代碼格式正確
        if not symbol.endswith('.TW') and not symbol.endswith('.TWO'):
            symbol = f"{symbol}.TW"
        
        # 並行獲取各類資料
        fundamental = TWSEService.get_fundamental_data(symbol)
        dividend = TWSEService.get_dividend_info(symbol)
        
        result = {
            "symbol": symbol,
            "fundamental": fundamental,
            "dividend": dividend
        }
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch comprehensive stock info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"取得綜合資訊失敗: {str(e)}"
        )
