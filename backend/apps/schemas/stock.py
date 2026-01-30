from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class StockBase(BaseModel):
    symbol: str
    name: str = "Unknown"
    market: str = "US"
    sector: Optional[str] = None

class StockCreate(StockBase):
    pass

class StockUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None

class StockResponse(StockBase):
    price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class WatchlistBase(BaseModel):
    symbol: str
    target_price: Optional[float] = None

class WatchlistCreate(WatchlistBase):
    pass

class WatchlistResponse(BaseModel):
    id: int
    user_id: str
    stock: StockResponse
    target_price: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
