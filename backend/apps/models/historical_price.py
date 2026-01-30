"""
Historical Price Data Model
用於緩存歷史價格數據，減少外部 API 調用
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, Date, Index
from sqlalchemy.dialects.postgresql import UUID
from apps.core.database import Base
from datetime import datetime

class HistoricalPrice(Base):
    __tablename__ = 'historical_prices'
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    date = Column(Date, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        # 唯一約束：同一股票同一天只能有一筆記錄
        Index('uq_symbol_date', 'symbol', 'date', unique=True),
        # 複合索引：優化查詢效能
        Index('idx_symbol_date_range', 'symbol', 'date'),
    )
