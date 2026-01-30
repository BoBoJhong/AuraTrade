from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field
from decimal import Decimal

from apps.core.database import get_db
from apps.core.dependencies import get_current_user
from apps.models.user import User

router = APIRouter(tags=["transactions"])


# Pydantic Models
class TransactionCreate(BaseModel):
    stock_symbol: str = Field(..., description="Stock symbol")
    transaction_type: str = Field(..., description="buy or sell")
    quantity: float = Field(..., gt=0, description="Number of shares")
    price: float = Field(..., gt=0, description="Price per share")
    commission: float = Field(0, ge=0, description="Commission fee")
    tax: float = Field(0, ge=0, description="Tax")
    transaction_date: date = Field(..., description="Transaction date")
    notes: Optional[str] = Field(None, max_length=500, description="Notes")

    class Config:
        json_schema_extra = {
            "example": {
                "stock_symbol": "2330.TW",
                "transaction_type": "buy",
                "quantity": 10,
                "price": 600.0,
                "commission": 42.0,
                "tax": 0,
                "transaction_date": "2026-01-30",
                "notes": "買入台積電"
            }
        }


class TransactionResponse(BaseModel):
    id: int
    user_id: str
    stock_symbol: str
    transaction_type: str
    quantity: float
    price: float
    commission: float
    tax: float
    total_amount: float
    transaction_date: date
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionSummary(BaseModel):
    total_buy_amount: float
    total_sell_amount: float
    total_commission: float
    total_tax: float
    net_profit_loss: float
    total_transactions: int


@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new transaction record"""
    try:
        # Calculate total amount
        if transaction.transaction_type == 'buy':
            total_amount = (transaction.price * transaction.quantity) + transaction.commission + transaction.tax
        else:  # sell
            total_amount = (transaction.price * transaction.quantity) - transaction.commission - transaction.tax

        # Create transaction
        from apps.models.stock import Transaction
        
        db_transaction = Transaction(
            user_id=current_user.user_id,
            stock_symbol=transaction.stock_symbol,
            transaction_type=transaction.transaction_type,
            quantity=transaction.quantity,
            price=transaction.price,
            commission=transaction.commission,
            tax=transaction.tax,
            total_amount=total_amount,
            transaction_date=transaction.transaction_date,
            notes=transaction.notes
        )

        db.add(db_transaction)
        await db.commit()
        await db.refresh(db_transaction)

        return db_transaction

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create transaction: {str(e)}")


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    symbol: Optional[str] = None,
    transaction_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's transaction history with optional filters"""
    from apps.models.stock import Transaction

    # Build query with filters
    query = select(Transaction).where(Transaction.user_id == current_user.user_id)

    if symbol:
        query = query.where(Transaction.stock_symbol == symbol)
    if transaction_type:
        query = query.where(Transaction.transaction_type == transaction_type)
    if start_date:
        query = query.where(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.where(Transaction.transaction_date <= end_date)

    query = query.order_by(Transaction.transaction_date.desc()).limit(limit)

    result = await db.execute(query)
    transactions = result.scalars().all()

    return transactions


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific transaction"""
    from apps.models.stock import Transaction

    result = await db.execute(
        select(Transaction).where(
            and_(
                Transaction.id == transaction_id,
                Transaction.user_id == current_user.user_id
            )
        )
    )
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return transaction


@router.delete("/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a transaction"""
    from apps.models.stock import Transaction

    result = await db.execute(
        select(Transaction).where(
            and_(
                Transaction.id == transaction_id,
                Transaction.user_id == current_user.user_id
            )
        )
    )
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    await db.delete(transaction)
    await db.commit()

    return {"message": "Transaction deleted successfully"}


@router.get("/transactions/summary/stats", response_model=TransactionSummary)
async def get_transaction_summary(
    symbol: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get transaction summary statistics"""
    from apps.models.stock import Transaction
    from sqlalchemy import func

    # Build query with filters
    query = select(Transaction).where(Transaction.user_id == current_user.user_id)

    if symbol:
        query = query.where(Transaction.stock_symbol == symbol)
    if start_date:
        query = query.where(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.where(Transaction.transaction_date <= end_date)

    result = await db.execute(query)
    transactions = result.scalars().all()

    # Calculate summary
    total_buy_amount = sum(t.total_amount for t in transactions if t.transaction_type == 'buy')
    total_sell_amount = sum(t.total_amount for t in transactions if t.transaction_type == 'sell')
    total_commission = sum(t.commission for t in transactions)
    total_tax = sum(t.tax for t in transactions)
    net_profit_loss = total_sell_amount - total_buy_amount

    return TransactionSummary(
        total_buy_amount=total_buy_amount,
        total_sell_amount=total_sell_amount,
        total_commission=total_commission,
        total_tax=total_tax,
        net_profit_loss=net_profit_loss,
        total_transactions=len(transactions)
    )