from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from apps.core.database import get_db
from apps.schemas.stock import WatchlistResponse, WatchlistCreate
from apps.models.stock import Watchlist, Stock
from apps.models.user import User
from apps.core.dependencies import get_current_user
from apps.core.services.yahoo_finance import YahooFinanceService

router = APIRouter(tags=["Watchlist"])

@router.get("/watchlist", response_model=List[WatchlistResponse])
async def get_my_watchlist(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's watchlist with latest prices
    """
    # 1. Get watchlist items with eager loading of stock relationship
    stmt = (
        select(Watchlist)
        .where(Watchlist.user_id == current_user.user_id)
        .options(selectinload(Watchlist.stock))
    )
    result = await db.execute(stmt)
    watchlist_items = result.scalars().all()
    
    # 2. Enrich with real-time prices
    response_items = []
    for item in watchlist_items:
        # Get price from Yahoo Finance
        price = await YahooFinanceService.get_stock_price(item.symbol)
        
        # Construct response (stock is now eagerly loaded, safe to access)
        stock_data = {
            "symbol": item.stock.symbol,
            "name": item.stock.name,
            "market": item.stock.market,
            "sector": item.stock.sector,
            "price": price
        }
        
        response_items.append({
            "id": item.id,
            "user_id": str(item.user_id),
            "stock": stock_data,
            "target_price": item.target_price,
            "created_at": item.created_at
        })
        
    return response_items

@router.post("/watchlist", response_model=WatchlistResponse)
async def add_to_watchlist(
    item_in: WatchlistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a stock to watchlist
    """
    # 1. Ensure stock exists locally
    stmt = select(Stock).where(Stock.symbol == item_in.symbol)
    result = await db.execute(stmt)
    stock = result.scalars().first()
    
    if not stock:
        # Try to fetch info to verify it exists and Create it
        info = await YahooFinanceService.get_stock_info(item_in.symbol)
        if not info:
             raise HTTPException(
                 status_code=404, 
                 detail={
                     "message": "無法找到此股票代碼",
                     "code": "STOCK_NOT_FOUND",
                     "hint": "請確認股票代碼是否正確，或稍後再試（Yahoo Finance API 可能暫時限流）"
                 }
             )
             
        stock = Stock(
            symbol=info['symbol'],
            name=info['name'],
            market=info['market'],
            sector=info.get('sector')
        )
        db.add(stock)
        try:
            await db.commit()
            await db.refresh(stock)
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create stock record")

    # 2. Create Watchlist Item
    # Store symbol before any DB operations that might fail
    stock_symbol = stock.symbol
    stock_name = stock.name
    
    watchlist_item = Watchlist(
        user_id=current_user.user_id,
        symbol=stock_symbol,
        target_price=item_in.target_price
    )
    
    try:
        db.add(watchlist_item)
        await db.commit()
        await db.refresh(watchlist_item)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=400, 
            detail={
                "message": f"股票 {stock_name} ({stock_symbol}) 已在您的自選股中",
                "code": "ALREADY_IN_WATCHLIST",
                "symbol": stock_symbol
            }
        )
    
    # Return formatted response
    price = await YahooFinanceService.get_stock_price(stock_symbol)
    
    stock_response = {
        "symbol": stock_symbol,
        "name": stock_name,
        "market": stock.market,
        "sector": stock.sector,
        "price": price
    }
    
    return {
        "id": watchlist_item.id,
        "user_id": str(watchlist_item.user_id),
        "stock": stock_response,
        "target_price": watchlist_item.target_price,
        "created_at": watchlist_item.created_at
    }

@router.delete("/watchlist/{symbol}")
async def remove_from_watchlist(
    symbol: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a stock from watchlist
    """
    stmt = select(Watchlist).where(
        Watchlist.user_id == current_user.user_id,
        Watchlist.symbol == symbol
    )
    result = await db.execute(stmt)
    item = result.scalars().first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
        
    await db.delete(item)
    await db.commit()
    
    return {"message": "Successfully removed from watchlist"}
