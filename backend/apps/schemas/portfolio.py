from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PositionResponse(BaseModel):
    id: int
    user_id: str
    symbol: str
    quantity: float
    buy_price: float
    current_price: Optional[float] = None
    cost: Optional[float] = None
    market_value: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_percent: Optional[float] = None
    
    class Config:
        from_attributes = True


class PortfolioSummary(BaseModel):
    total_positions: int
    total_cost: float
    total_market_value: float
    total_profit_loss: float
    total_profit_loss_percent: float
    positions: list[PositionResponse]


class PriceAlertCreate(BaseModel):
    symbol: str
    alert_type: str
    target_value: float
    base_price: Optional[float] = None
    message: Optional[str] = None


class PriceAlertResponse(BaseModel):
    id: int
    user_id: str
    symbol: str
    alert_type: str
    target_value: float
    base_price: Optional[float]
    is_active: int
    is_triggered: int
    triggered_at: Optional[datetime]
    message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
