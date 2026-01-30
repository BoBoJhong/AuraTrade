from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from typing import List
from apps.core.dependencies import get_current_user, get_db
from apps.models.user import User
from apps.models.transaction import Transaction
from apps.models.stock import Stock
from apps.schemas.transaction import TransactionCreate, TransactionResponse, TransactionStats
import logging

router = APIRouter(prefix="/transactions", tags=["transactions"])
logger = logging.getLogger(__name__)


@router.post("", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 檢查股票是否存在
        stmt = select(Stock).where(Stock.symbol == transaction.stock_symbol)
        result = await db.execute(stmt)
        stock = result.scalar_one_or_none()
        
        if not stock:
            stock = Stock(
                symbol=transaction.stock_symbol,
                name=transaction.stock_symbol,
                market="Unknown",
                industry="Unknown"
            )
            db.add(stock)
            await db.commit()
        
        # 計算總金額
        if transaction.transaction_type == "buy":
            total_amount = (transaction.quantity * transaction.price) + transaction.commission + transaction.tax
        else:
            total_amount = (transaction.quantity * transaction.price) - transaction.commission - transaction.tax
        
        # 建立交易記錄
        db_transaction = Transaction(
            user_id=current_user.user_id,
            stock_symbol=transaction.stock_symbol,
            transaction_type=transaction.transaction_type,
            quantity=transaction.quantity,
            price=transaction.price,
            commission=transaction.commission or 0,
            tax=transaction.tax or 0,
            total_amount=total_amount,
            transaction_date=transaction.transaction_date,
            notes=transaction.notes
        )
        
        db.add(db_transaction)
        await db.commit()
        await db.refresh(db_transaction)
        
        logger.info(f"User {current_user.user_id} created transaction {db_transaction.id}")
        return db_transaction
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"建立交易記錄失敗: {str(e)}")


@router.get("", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        stmt = select(Transaction).where(
            Transaction.user_id == current_user.user_id
        ).order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        transactions = result.scalars().all()
        
        return transactions
        
    except Exception as e:
        logger.error(f"Error fetching transactions: {str(e)}")
        raise HTTPException(status_code=500, detail="獲取交易記錄失敗")


@router.get("/stats", response_model=TransactionStats)
async def get_transaction_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        stmt = select(Transaction).where(Transaction.user_id == current_user.user_id)
        result = await db.execute(stmt)
        transactions = result.scalars().all()
        
        total_buy = sum(t.total_amount for t in transactions if t.transaction_type == "buy")
        total_sell = sum(t.total_amount for t in transactions if t.transaction_type == "sell")
        
        stats = TransactionStats(
            total_transactions=len(transactions),
            total_buy_amount=total_buy,
            total_sell_amount=total_sell,
            net_profit=total_sell - total_buy,
            realized_profit=total_sell - total_buy
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Error fetching transaction stats: {str(e)}")
        raise HTTPException(status_code=500, detail="獲取統計資料失敗")


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        stmt = select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.user_id
        )
        result = await db.execute(stmt)
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="找不到該交易記錄")
        
        await db.delete(transaction)
        await db.commit()
        
        logger.info(f"User {current_user.user_id} deleted transaction {transaction_id}")
        return {"message": "交易記錄已刪除"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting transaction: {str(e)}")
        raise HTTPException(status_code=500, detail="刪除交易記錄失敗")
