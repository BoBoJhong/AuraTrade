"""
Core Configuration
追溯: REQ-092, REQ-093
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """應用程式設定 - 追溯: SDD Section 3.1"""
    
    # Application
    APP_NAME: str = "AuraTrade"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/auratrade"
    DB_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # External APIs
    GEMINI_API_KEY: str = ""
    LINE_CHANNEL_ACCESS_TOKEN: str = ""
    LINE_CHANNEL_SECRET: str = ""  # LINE Bot Webhook 簽名驗證用
    YAHOO_FINANCE_API_KEY: str = ""
    FUGLE_API_KEY: str = ""  # Fugle MarketData API Key for Taiwan stocks
    ALPHA_VANTAGE_API_KEY: str = ""  # Alpha Vantage API Key for US stocks & technical indicators
    
    # Rate Limiting - BR-03, BR-04
    AI_DAILY_LIMIT: int = 20
    NOTIFICATION_DAILY_LIMIT: int = 50
    
    # Business Rules
    MAX_WATCHLIST_SIZE: int = 50  # BR-01
    STOCK_UPDATE_INTERVAL_SECONDS: int = 2  # BR-02
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
