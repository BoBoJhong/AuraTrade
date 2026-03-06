from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Index, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from apps.core.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class AIRecommendation(Base):
    """AI 股票推薦歷史紀錄"""
    __tablename__ = "ai_recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 股票資訊
    symbol = Column(String(20), nullable=False, index=True)
    stock_name = Column(String(100), nullable=False)
    market = Column(String(10), nullable=False)  # TW or US
    
    # 推薦時的價格
    price = Column(Float, nullable=False)
    
    # AI 評分與推薦
    ai_score = Column(Float, nullable=False)  # 0-100
    recommendation = Column(String(20), nullable=False)  # 買入/觀望/賣出
    confidence = Column(Float, nullable=False)  # 0-100 信心度
    
    # 評分細項
    technical_score = Column(Float, nullable=False)  # 技術面分數
    fundamental_score = Column(Float, nullable=False)  # 基本面分數
    sentiment_score = Column(Float, nullable=False)  # 情緒面分數
    
    # 推薦理由
    reasons = Column(JSON, nullable=False)  # ["理由1", "理由2", ...]
    
    # 技術指標快照
    technical_indicators = Column(JSON, nullable=True)  # {rsi: 45, macd: 0.5, ...}
    
    # 基本面指標快照
    fundamental_data = Column(JSON, nullable=True)  # {pe: 15, roe: 18, ...}
    
    # 新聞情緒
    news_sentiment = Column(String(20), nullable=True)  # 正面/中性/負面
    latest_news = Column(JSON, nullable=True)  # [{"title": "...", "url": "..."}]
    
    # 回測數據（後續更新）
    price_after_7d = Column(Float, nullable=True)  # 7天後價格
    price_after_30d = Column(Float, nullable=True)  # 30天後價格
    return_7d = Column(Float, nullable=True)  # 7天報酬率
    return_30d = Column(Float, nullable=True)  # 30天報酬率
    accuracy_label = Column(String(20), nullable=True)  # 準確/不準確
    
    # 時間戳記
    recommended_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 索引
    __table_args__ = (
        Index('idx_symbol_recommended_at', 'symbol', 'recommended_at'),
        Index('idx_recommendation', 'recommendation'),
        Index('idx_ai_score', 'ai_score'),
        Index('idx_market', 'market'),
    )
    
    def __repr__(self):
        return f"<AIRecommendation {self.symbol} {self.recommendation} score={self.ai_score}>"
