from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from apps.core.database import Base

class Stock(Base):
    """
    股票基礎資訊模型
    只儲存基本資料，即時價格走勢透過 Redis 或 API 即時獲取
    """
    __tablename__ = "stocks"

    symbol = Column(String(20), primary_key=True, index=True, comment="股票代碼 (e.g. 2330.TW)")
    name = Column(String(100), nullable=False, comment="股票名稱")
    market = Column(String(10), nullable=False, comment="市場 (TW, US)")
    sector = Column(String(50), nullable=True, comment="產業類別")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    watchlists = relationship("Watchlist", back_populates="stock", cascade="all, delete-orphan")

class Watchlist(Base):
    """
    用戶自選股關聯表
    """
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(20), ForeignKey("stocks.symbol", ondelete="CASCADE"), nullable=False)
    target_price = Column(Float, nullable=True, comment="目標價格 (預警用)")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("apps.models.user.User", backref="watchlists")
    stock = relationship("Stock", back_populates="watchlists")

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'symbol', name='uq_user_stock'),
    )
