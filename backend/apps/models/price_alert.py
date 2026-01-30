from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Integer, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from apps.core.database import Base
import enum

class AlertType(str, enum.Enum):
    """Alert type enumeration"""
    PRICE_ABOVE = "price_above"  # 價格達到或超過
    PRICE_BELOW = "price_below"  # 價格達到或低於
    PERCENT_UP = "percent_up"    # 上漲百分比
    PERCENT_DOWN = "percent_down" # 下跌百分比

class PriceAlert(Base):
    """
    價格提醒模型
    用戶可設定目標價格或百分比，達到條件時發送通知
    """
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(20), ForeignKey("stocks.symbol", ondelete="CASCADE"), nullable=False)
    
    alert_type = Column(String(20), nullable=False, comment="提醒類型")
    target_value = Column(Float, nullable=False, comment="目標值（價格或百分比）")
    base_price = Column(Float, nullable=True, comment="基準價格（用於百分比計算）")
    
    is_active = Column(Boolean, default=True, comment="是否啟用")
    is_triggered = Column(Boolean, default=False, comment="是否已觸發")
    triggered_at = Column(DateTime, nullable=True, comment="觸發時間")
    
    message = Column(String(255), nullable=True, comment="自定義訊息")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("apps.models.user.User", backref="price_alerts")
    stock = relationship("Stock", backref="price_alerts")