from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from apps.core.database import Base
from datetime import datetime

class Position(Base):
    """持倉記錄模型"""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(20), ForeignKey("stocks.symbol", ondelete="CASCADE"), nullable=False)
    
    # 持倉資訊
    quantity = Column(Float, nullable=False, comment="持有數量")
    buy_price = Column(Float, nullable=False, comment="買入均價")
    buy_date = Column(DateTime, nullable=False, comment="買入日期")
    
    # 可選資訊
    notes = Column(String(500), nullable=True, comment="備註")
    
    # 時間戳記
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    user = relationship("User", backref="positions")
    stock = relationship("Stock", backref="positions")
    
    def __repr__(self):
        return f"<Position(id={self.id}, user_id={self.user_id}, symbol={self.symbol}, quantity={self.quantity})>"
