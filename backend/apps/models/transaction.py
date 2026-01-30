from sqlalchemy import Column, Integer, String, Float, Date, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from apps.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    stock_symbol = Column(String(20), ForeignKey("stocks.symbol", ondelete="CASCADE"), nullable=False, index=True)
    transaction_type = Column(String(10), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    commission = Column(Float, default=0)
    tax = Column(Float, default=0)
    total_amount = Column(Float, nullable=False)
    transaction_date = Column(Date, nullable=False, index=True)
    notes = Column(String(500), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

