"""
Integration Test Configuration
整合測試配置 - 提供測試客戶端、資料庫和認證 fixtures

注意：為了測試隔離，我們 Mock 外部依賴以避免導入問題
"""
import sys
from unittest.mock import MagicMock

# Mock 有問題的依賴模組，避免 Python 3.14 兼容性問題
sys.modules['yfinance'] = MagicMock()
sys.modules['curl_cffi'] = MagicMock()
sys.modules['eventlet'] = MagicMock()

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator, Dict
import os
from datetime import datetime

# Import FastAPI app and database
from apps.core.database import Base, get_db
from main import app


# Test Database URL (使用 SQLite 進行測試，避免需要 PostgreSQL)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite+aiosqlite:///:memory:"  # 使用記憶體資料庫，每次測試獨立
)


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """建立測試資料庫引擎"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,  # 不使用連線池，確保每個測試獨立
        echo=False
    )
    
    # 建立所有表格
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # 測試後清理
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """建立測試用資料庫 session"""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """建立測試用 HTTP 客戶端"""
    from httpx import ASGITransport
    
    # Override database dependency
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    # 使用 ASGITransport 而非廢棄的 app 參數
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Clean up overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_user(client: AsyncClient) -> Dict[str, str]:
    """建立測試用戶並返回認證 token"""
    # 註冊測試用戶
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    user_data = {
        "email": f"test_{timestamp}@example.com",
        "username": f"testuser_{timestamp}",
        "password": "Test123456!",
        "confirm_password": "Test123456!"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201, f"註冊失敗: {response.text}"
    
    result = response.json()
    
    return {
        "user_id": result.get("user_id"),
        "email": user_data["email"],
        "username": user_data["username"],
        "password": user_data["password"],
        "access_token": result.get("access_token"),
        "token_type": result.get("token_type", "bearer")
    }


@pytest_asyncio.fixture(scope="function")
async def auth_headers(test_user: Dict[str, str]) -> Dict[str, str]:
    """返回認證標頭"""
    return {
        "Authorization": f"{test_user['token_type']} {test_user['access_token']}"
    }


@pytest.fixture(scope="session")
def test_stock_symbols():
    """提供測試用股票代碼"""
    return {
        "tw": ["2330.TW", "2317.TW", "2454.TW"],  # 台股
        "us": ["AAPL", "MSFT", "GOOGL"],  # 美股
        "invalid": ["INVALID123", "XXX.TW"]  # 無效代碼
    }


@pytest.fixture(scope="session")
def sample_stock_data():
    """提供樣本股票數據"""
    return {
        "symbol": "2330.TW",
        "name": "台積電",
        "price": 500.0,
        "change": 5.0,
        "change_percent": 1.01,
        "volume": 50000000,
        "market_cap": 13000000000000
    }


# ============================================================
# Priority 1 改進: Mock 外部依賴 Fixtures
# ============================================================

@pytest.fixture
def mock_yahoo_finance(monkeypatch):
    """
    Mock Yahoo Finance API 回應
    
    根據 IMPROVEMENTS.md Priority 1 實施
    避免測試依賴外部 API，提升速度和穩定性
    """
    from tests.factories import MockDataFactory
    
    class MockYahooService:
        """Mock Yahoo Finance 服務"""
        
        async def get_quote(self, symbol: str):
            """Mock 獲取即時報價"""
            return MockDataFactory.create_yahoo_quote_response(symbol)
        
        async def get_history(self, symbol: str, period: str = "1mo", interval: str = "1d"):
            """Mock 獲取歷史數據"""
            days_map = {"5d": 5, "1mo": 30, "3mo": 90, "6mo": 180, "1y": 365}
            days = days_map.get(period, 30)
            return MockDataFactory.create_yahoo_history_response(symbol, days)
        
        async def search_stocks(self, query: str):
            """Mock 搜尋股票"""
            return [
                {"symbol": "2330.TW", "name": "台積電", "market": "TW"},
                {"symbol": "AAPL", "name": "Apple Inc.", "market": "US"}
            ]
    
    return MockYahooService()


@pytest.fixture
def mock_gemini_ai(monkeypatch):
    """
    Mock Gemini AI 服務
    
    根據 IMPROVEMENTS.md Priority 1 實施
    """
    from tests.factories import MockDataFactory
    
    class MockGeminiService:
        """Mock Gemini AI 服務"""
        
        def is_available(self):
            """Mock 服務可用性"""
            return True
        
        async def analyze_news_sentiment(self, title: str, summary: str = ""):
            """Mock 新聞情緒分析"""
            # 根據標題關鍵字返回不同情緒
            title_lower = title.lower()
            
            if any(word in title_lower for word in ["上漲", "突破", "創新高", "利多"]):
                sentiment = "positive"
                score = 0.85
            elif any(word in title_lower for word in ["下跌", "暴跌", "利空", "虧損"]):
                sentiment = "negative"
                score = -0.75
            else:
                sentiment = "neutral"
                score = 0.0
            
            return MockDataFactory.create_gemini_sentiment_response(sentiment, score)
        
        async def generate_investment_advice(self, symbol: str, action: str):
            """Mock 投資建議生成"""
            return {
                "symbol": symbol,
                "action": action,
                "advice": "這是 AI 生成的投資建議 (Mock)",
                "confidence": 0.85
            }
    
    return MockGeminiService()


@pytest.fixture
def mock_technical_indicators(monkeypatch):
    """
    Mock 技術指標服務
    
    根據 IMPROVEMENTS.md Priority 1 實施
    """
    from tests.factories import MockDataFactory
    
    class MockTechnicalIndicatorService:
        """Mock 技術指標服務"""
        
        async def calculate_ma(self, data, periods):
            """Mock 計算移動均線"""
            return {f"ma{p}": 500.0 - p for p in periods}
        
        async def calculate_macd(self, data):
            """Mock 計算 MACD"""
            return {"macd": 2.5, "signal": 1.8, "histogram": 0.7}
        
        async def calculate_rsi(self, data, period=14):
            """Mock 計算 RSI"""
            return 65.5
        
        async def calculate_kdj(self, data):
            """Mock 計算 KDJ"""
            return {"k": 75.2, "d": 72.8, "j": 80.0}
        
        async def calculate_all_indicators(self, data):
            """Mock 計算所有指標"""
            return MockDataFactory.create_technical_indicators_response()
    
    return MockTechnicalIndicatorService()

