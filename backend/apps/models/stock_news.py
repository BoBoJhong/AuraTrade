from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Index
from sqlalchemy.sql import func
from apps.core.database import Base

class StockNews(Base):
    """Stock News Model"""
    __tablename__ = "stock_news"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    source = Column(String(100), nullable=False)
    url = Column(String(1000), nullable=False, unique=True)
    published_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # AI Analysis Fields
    sentiment = Column(String(20), nullable=True)  # positive, negative, neutral
    sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_symbol_published', 'symbol', 'published_at'),
        Index('idx_published_at', 'published_at'),
    )
