from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_
from sqlalchemy.orm import selectinload
from apps.core.database import get_db
from apps.models.price_alert import PriceAlert, AlertType
from apps.models.user import User
from apps.models.stock import Stock
from apps.core.dependencies import get_current_user
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

router = APIRouter(tags=["Price Alerts"])

# Schemas
class AlertCreate(BaseModel):
    symbol: str = Field(..., description="股票代碼 (e.g. 2330.TW)")
    alert_type: AlertType = Field(..., description="提醒類型")
    target_value: float = Field(..., description="目標值 (價格或百分比)")
    base_price: float | None = Field(None, description="基準價格 (百分比提醒用)")
    message: str | None = Field(None, description="自訂提醒訊息")

class AlertUpdate(BaseModel):
    is_active: bool | None = None
    target_value: float | None = None
    message: str | None = None

class AlertResponse(BaseModel):
    id: int
    user_id: UUID
    symbol: str
    alert_type: str
    target_value: float
    base_price: float | None
    is_active: bool
    is_triggered: bool
    triggered_at: datetime | None
    message: str | None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/alerts", response_model=List[AlertResponse])
async def get_my_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    active_only: bool = True
):
    """
    取得當前用戶的價格提醒
    - active_only: 是否只顯示啟用中的提醒（預設 True）
    """
    stmt = select(PriceAlert).where(PriceAlert.user_id == current_user.user_id)
    
    if active_only:
        stmt = stmt.where(PriceAlert.is_active == True)
    
    stmt = stmt.order_by(PriceAlert.created_at.desc())
    result = await db.execute(stmt)
    alerts = result.scalars().all()
    
    return alerts

@router.post("/alerts", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_in: AlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    建立價格提醒
    
    提醒類型說明：
    - price_above: 價格達到或超過 target_value
    - price_below: 價格達到或低於 target_value
    - percent_up: 相對於 base_price 上漲 target_value%
    - percent_down: 相對於 base_price 下跌 target_value%
    
    百分比類型提醒必須提供 base_price
    """
    # 驗證股票是否存在
    stmt = select(Stock).where(Stock.symbol == alert_in.symbol)
    result = await db.execute(stmt)
    stock = result.scalars().first()
    
    if not stock:
        raise HTTPException(
            status_code=404,
            detail=f"股票代碼 {alert_in.symbol} 不存在，請先加入自選股"
        )
    
    # 驗證百分比類型必須有 base_price
    if alert_in.alert_type in [AlertType.PERCENT_UP, AlertType.PERCENT_DOWN]:
        if not alert_in.base_price or alert_in.base_price <= 0:
            raise HTTPException(
                status_code=400,
                detail="百分比類型提醒必須提供有效的 base_price"
            )
    
    # 建立提醒
    alert = PriceAlert(
        user_id=current_user.user_id,
        symbol=alert_in.symbol,
        alert_type=alert_in.alert_type.value,
        target_value=alert_in.target_value,
        base_price=alert_in.base_price,
        message=alert_in.message
    )
    
    db.add(alert)
    try:
        await db.commit()
        await db.refresh(alert)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"建立提醒失敗: {str(e)}")
    
    return alert

@router.patch("/alerts/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新價格提醒（可啟用/停用、修改目標值、修改訊息）
    """
    # 查詢提醒
    stmt = select(PriceAlert).where(
        and_(
            PriceAlert.id == alert_id,
            PriceAlert.user_id == current_user.user_id
        )
    )
    result = await db.execute(stmt)
    alert = result.scalars().first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="提醒不存在")
    
    # 更新欄位
    if alert_update.is_active is not None:
        alert.is_active = alert_update.is_active
    if alert_update.target_value is not None:
        alert.target_value = alert_update.target_value
    if alert_update.message is not None:
        alert.message = alert_update.message
    
    alert.updated_at = datetime.utcnow()
    
    try:
        await db.commit()
        await db.refresh(alert)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"更新提醒失敗: {str(e)}")
    
    return alert

@router.delete("/alerts/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    刪除價格提醒
    """
    stmt = delete(PriceAlert).where(
        and_(
            PriceAlert.id == alert_id,
            PriceAlert.user_id == current_user.user_id
        )
    )
    result = await db.execute(stmt)
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="提醒不存在")
    
    await db.commit()
    return None

@router.get("/alerts/stock/{symbol}", response_model=List[AlertResponse])
async def get_alerts_by_stock(
    symbol: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取得特定股票的所有提醒
    """
    stmt = (
        select(PriceAlert)
        .where(
            and_(
                PriceAlert.user_id == current_user.user_id,
                PriceAlert.symbol == symbol
            )
        )
        .order_by(PriceAlert.created_at.desc())
    )
    result = await db.execute(stmt)
    alerts = result.scalars().all()
    
    return alerts

@router.post("/alerts/check")
async def check_and_trigger_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    檢查並觸發價格提醒
    遍歷所有啟用中且未觸發的提醒，檢查是否達到條件
    """
    from apps.core.services.yahoo_finance import YahooFinanceService
    
    # 獲取所有啟用中且未觸發的提醒
    stmt = select(PriceAlert).where(
        and_(
            PriceAlert.user_id == current_user.user_id,
            PriceAlert.is_active == True,
            PriceAlert.is_triggered == False
        )
    )
    result = await db.execute(stmt)
    alerts = result.scalars().all()
    
    triggered_count = 0
    
    for alert in alerts:
        try:
            # 獲取當前價格
            current_price = await YahooFinanceService.get_stock_price(alert.symbol)
            
            if not current_price:
                continue
            
            should_trigger = False
            
            # 檢查觸發條件
            if alert.alert_type == AlertType.PRICE_ABOVE.value:
                should_trigger = current_price >= alert.target_value
            elif alert.alert_type == AlertType.PRICE_BELOW.value:
                should_trigger = current_price <= alert.target_value
            elif alert.alert_type == AlertType.PERCENT_UP.value:
                if alert.base_price:
                    percent_change = ((current_price - alert.base_price) / alert.base_price) * 100
                    should_trigger = percent_change >= alert.target_value
            elif alert.alert_type == AlertType.PERCENT_DOWN.value:
                if alert.base_price:
                    percent_change = ((alert.base_price - current_price) / alert.base_price) * 100
                    should_trigger = percent_change >= alert.target_value
            
            # 觸發提醒
            if should_trigger:
                alert.is_triggered = True
                alert.triggered_at = datetime.utcnow()
                triggered_count += 1
                
        except Exception as e:
            print(f"檢查提醒 {alert.id} 時發生錯誤: {str(e)}")
            continue
    
    # 提交變更
    await db.commit()
    
    return {
        "checked": len(alerts),
        "triggered": triggered_count,
        "message": f"已檢查 {len(alerts)} 個提醒，觸發 {triggered_count} 個"
    }
