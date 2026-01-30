from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class TransactionCreate(BaseModel):
    stock_symbol: str = Field(..., description="股票代碼")
    transaction_type: str = Field(..., description="交易類型: buy 或 sell")
    quantity: float = Field(..., gt=0, description="交易股數")
    price: float = Field(..., gt=0, description="成交價格")
    commission: Optional[float] = Field(0, description="手續費")
    tax: Optional[float] = Field(0, description="交易稅")
    transaction_date: date = Field(..., description="交易日期")
    notes: Optional[str] = Field(None, description="備註")


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
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionStats(BaseModel):
    total_transactions: int
    total_buy_amount: float
    total_sell_amount: float
    net_profit: float
    realized_profit: float
