from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_
from apps.core.database import get_db
from apps.models.position import Position
from apps.models.user import User
from apps.models.stock import Stock
from apps.core.dependencies import get_current_user
from apps.core.services.yahoo_finance import YahooFinanceService
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

router = APIRouter(tags=["Positions"])

# Schemas
class PositionCreate(BaseModel):
    symbol: str = Field(..., description="股票代碼")
    quantity: float = Field(..., gt=0, description="持有數量")
    buy_price: float = Field(..., gt=0, description="買入均價")
    buy_date: datetime = Field(..., description="買入日期")
    notes: str | None = Field(None, description="備註")

class PositionUpdate(BaseModel):
    quantity: float | None = Field(None, gt=0)
    buy_price: float | None = Field(None, gt=0)
    buy_date: datetime | None = None
    notes: str | None = None

class PositionResponse(BaseModel):
    id: int
    user_id: UUID
    symbol: str
    quantity: float
    buy_price: float
    buy_date: datetime
    notes: str | None
    created_at: datetime
    updated_at: datetime
    
    # 計算欄位
    current_price: float | None = None
    market_value: float | None = None
    cost: float = 0
    profit_loss: float = 0
    profit_loss_percent: float = 0
    
    class Config:
        from_attributes = True

@router.get("/positions", response_model=List[PositionResponse])
async def get_my_positions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取得當前用戶的所有持倉
    """
    stmt = select(Position).where(Position.user_id == current_user.user_id)
    result = await db.execute(stmt)
    positions = result.scalars().all()
    
    # 豐富化資料（加入當前價格和計算損益）
    enriched_positions = []
    for pos in positions:
        current_price = await YahooFinanceService.get_stock_price(pos.symbol)
        
        cost = pos.quantity * pos.buy_price
        market_value = pos.quantity * current_price if current_price else 0
        profit_loss = market_value - cost
        profit_loss_percent = (profit_loss / cost * 100) if cost > 0 else 0
        
        pos_data = PositionResponse(
            id=pos.id,
            user_id=pos.user_id,
            symbol=pos.symbol,
            quantity=pos.quantity,
            buy_price=pos.buy_price,
            buy_date=pos.buy_date,
            notes=pos.notes,
            created_at=pos.created_at,
            updated_at=pos.updated_at,
            current_price=current_price,
            market_value=market_value,
            cost=cost,
            profit_loss=profit_loss,
            profit_loss_percent=profit_loss_percent
        )
        enriched_positions.append(pos_data)
    
    return enriched_positions

@router.post("/positions", response_model=PositionResponse, status_code=status.HTTP_201_CREATED)
async def create_position(
    position_in: PositionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    建立新持倉記錄
    """
    # 驗證股票是否存在
    stmt = select(Stock).where(Stock.symbol == position_in.symbol)
    result = await db.execute(stmt)
    stock = result.scalars().first()
    
    if not stock:
        raise HTTPException(
            status_code=404,
            detail=f"股票代碼 {position_in.symbol} 不存在，請先加入自選股"
        )
    
    # 建立持倉
    position = Position(
        user_id=current_user.user_id,
        symbol=position_in.symbol,
        quantity=position_in.quantity,
        buy_price=position_in.buy_price,
        buy_date=position_in.buy_date,
        notes=position_in.notes
    )
    
    db.add(position)
    try:
        await db.commit()
        await db.refresh(position)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"建立持倉失敗: {str(e)}")
    
    # 計算損益
    current_price = await YahooFinanceService.get_stock_price(position.symbol)
    cost = position.quantity * position.buy_price
    market_value = position.quantity * current_price if current_price else 0
    profit_loss = market_value - cost
    profit_loss_percent = (profit_loss / cost * 100) if cost > 0 else 0
    
    return PositionResponse(
        id=position.id,
        user_id=position.user_id,
        symbol=position.symbol,
        quantity=position.quantity,
        buy_price=position.buy_price,
        buy_date=position.buy_date,
        notes=position.notes,
        created_at=position.created_at,
        updated_at=position.updated_at,
        current_price=current_price,
        market_value=market_value,
        cost=cost,
        profit_loss=profit_loss,
        profit_loss_percent=profit_loss_percent
    )

@router.patch("/positions/{position_id}", response_model=PositionResponse)
async def update_position(
    position_id: int,
    position_update: PositionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新持倉記錄
    """
    stmt = select(Position).where(
        and_(
            Position.id == position_id,
            Position.user_id == current_user.user_id
        )
    )
    result = await db.execute(stmt)
    position = result.scalars().first()
    
    if not position:
        raise HTTPException(status_code=404, detail="持倉記錄不存在")
    
    # 更新欄位
    if position_update.quantity is not None:
        position.quantity = position_update.quantity
    if position_update.buy_price is not None:
        position.buy_price = position_update.buy_price
    if position_update.buy_date is not None:
        position.buy_date = position_update.buy_date
    if position_update.notes is not None:
        position.notes = position_update.notes
    
    position.updated_at = datetime.utcnow()
    
    try:
        await db.commit()
        await db.refresh(position)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"更新持倉失敗: {str(e)}")
    
    # 計算損益
    current_price = await YahooFinanceService.get_stock_price(position.symbol)
    cost = position.quantity * position.buy_price
    market_value = position.quantity * current_price if current_price else 0
    profit_loss = market_value - cost
    profit_loss_percent = (profit_loss / cost * 100) if cost > 0 else 0
    
    return PositionResponse(
        id=position.id,
        user_id=position.user_id,
        symbol=position.symbol,
        quantity=position.quantity,
        buy_price=position.buy_price,
        buy_date=position.buy_date,
        notes=position.notes,
        created_at=position.created_at,
        updated_at=position.updated_at,
        current_price=current_price,
        market_value=market_value,
        cost=cost,
        profit_loss=profit_loss,
        profit_loss_percent=profit_loss_percent
    )

@router.delete("/positions/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_position(
    position_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    刪除持倉記錄
    """
    stmt = delete(Position).where(
        and_(
            Position.id == position_id,
            Position.user_id == current_user.user_id
        )
    )
    result = await db.execute(stmt)
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="持倉記錄不存在")
    
    await db.commit()
    return None

@router.get("/positions/summary")
async def get_portfolio_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取得投資組合總覽
    """
    stmt = select(Position).where(Position.user_id == current_user.user_id)
    result = await db.execute(stmt)
    positions = result.scalars().all()
    
    total_cost = 0
    total_market_value = 0
    
    for pos in positions:
        current_price = await YahooFinanceService.get_stock_price(pos.symbol)
        cost = pos.quantity * pos.buy_price
        market_value = pos.quantity * current_price if current_price else 0
        
        total_cost += cost
        total_market_value += market_value
    
    total_profit_loss = total_market_value - total_cost
    total_profit_loss_percent = (total_profit_loss / total_cost * 100) if total_cost > 0 else 0
    
    return {
        "total_positions": len(positions),
        "total_cost": total_cost,
        "total_market_value": total_market_value,
        "total_profit_loss": total_profit_loss,
        "total_profit_loss_percent": total_profit_loss_percent
    }
