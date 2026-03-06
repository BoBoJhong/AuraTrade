"""
Pytest Configuration & Global Fixtures
AuraTrade Backend Testing

此檔案解決測試執行路徑問題，提供全域測試配置與共用 fixtures。
"""

import sys
import os
from pathlib import Path
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
import redis.asyncio as redis

# === 路徑配置 (解決 import 問題) ===

# 將 backend 目錄加入 Python 路徑
BACKEND_DIR = Path(__file__).parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

PROJECT_ROOT = BACKEND_DIR.parent
TESTS_DIR = PROJECT_ROOT / "tests"

# 導入專案模組 (現在路徑已正確)
from apps.core.database import Base
from apps.core.config import settings


# === Pytest 配置 ===

def pytest_configure(config):
    """Pytest 初始化配置"""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests"
    )
    config.addinivalue_line(
        "markers", "performance: Performance tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers", "critical: Critical path tests"
    )


def pytest_collection_modifyitems(config, items):
    """自動標記測試"""
    for item in items:
        # 根據測試路徑自動添加標記
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        
        # 標記慢速測試
        if "slow" in item.nodeid:
            item.add_marker(pytest.mark.slow)


# === Event Loop Fixture (Async 測試支援) ===

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# === 測試資料庫 Fixtures ===

@pytest.fixture(scope="session")
async def test_engine():
    """測試用資料庫引擎 (使用 SQLite in-memory)"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=NullPool,
        echo=False  # 測試時關閉 SQL log
    )
    
    # 建立所有表格
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # 清理
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """測試用資料庫 Session (每次測試後自動清理)"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()  # 測試後回滾


# === Redis Fixtures ===

@pytest.fixture(scope="session")
async def test_redis():
    """測試用 Redis 客戶端 (使用 FakeRedis)"""
    try:
        from fakeredis import aioredis as fakeredis
        redis_client = fakeredis.FakeRedis(decode_responses=True)
    except ImportError:
        # 如果沒有 fakeredis，使用真實 Redis (需先啟動)
        redis_client = await redis.from_url(
            "redis://localhost:6379/15",  # 使用 db 15 避免污染
            decode_responses=True
        )
    
    yield redis_client
    
    # 清理
    await redis_client.flushdb()
    await redis_client.close()


# === 測試用戶 Fixtures ===

@pytest.fixture
def test_user_data():
    """測試用戶基本資料"""
    return {
        "email": "test@example.com",
        "password": "TestPass123",
        "username": "testuser"
    }


@pytest.fixture
async def test_user(test_db, test_user_data):
    """建立測試用戶於資料庫"""
    from apps.models.user import User
    from apps.core.security import hash_password
    
    user = User(
        email=test_user_data["email"],
        username=test_user_data["username"],
        password_hash=hash_password(test_user_data["password"]),
        is_active=True
    )
    
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    return user


@pytest.fixture
def test_token(test_user):
    """生成測試用 JWT Token"""
    from apps.core.security import create_access_token
    
    return create_access_token({
        "sub": str(test_user.user_id),
        "email": test_user.email,
        "role": test_user.role
    })


# === HTTP Client Fixtures ===

@pytest.fixture
async def async_client():
    """Async HTTP 客戶端 (測試 API 用)"""
    import httpx
    from main import app
    
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def auth_headers(test_token):
    """認證 Headers"""
    return {"Authorization": f"Bearer {test_token}"}


# === Mock Fixtures ===

@pytest.fixture
def mock_yahoo_finance(mocker):
    """Mock Yahoo Finance API"""
    mock_data = {
        "symbol": "2330.TW",
        "name": "台積電",
        "price": 580.0,
        "change": 5.0,
        "change_percent": 0.87
    }
    
    mock = mocker.patch(
        "apps.core.services.yahoo_finance.YahooFinanceService.get_stock_data"
    )
    mock.return_value = mock_data
    
    return mock


@pytest.fixture
def mock_gemini_ai(mocker):
    """Mock Gemini AI API"""
    mock_response = {
        "sentiment": "positive",
        "sentiment_score": 0.8,
        "reasoning": "股價上漲，營收成長"
    }
    
    mock = mocker.patch(
        "apps.core.services.gemini_service.GeminiService.analyze_news_sentiment"
    )
    mock.return_value = mock_response
    
    return mock


# === 時間 Fixtures ===

@pytest.fixture
def freeze_time():
    """凍結時間 (用於測試時間相關邏輯)"""
    from freezegun import freeze_time
    return freeze_time


# === 測試數據 Fixtures ===

@pytest.fixture
def sample_stock_data():
    """範例股票數據"""
    return [
        {"date": "2024-01-01", "close": 580.0, "volume": 1000000},
        {"date": "2024-01-02", "close": 585.0, "volume": 1200000},
        {"date": "2024-01-03", "close": 575.0, "volume": 900000},
        {"date": "2024-01-04", "close": 590.0, "volume": 1500000},
        {"date": "2024-01-05", "close": 595.0, "volume": 1300000},
    ]


# === 清理 Fixtures ===

@pytest.fixture(autouse=True)
async def cleanup_after_test():
    """每次測試後自動清理"""
    yield
    # 測試後清理邏輯
    # 例如：清理暫存檔案、重置 Mock 等


# === 測試標記 Helpers ===

def requires_db(func):
    """標記需要資料庫的測試"""
    return pytest.mark.requires_db(func)


def requires_api(func):
    """標記需要外部 API 的測試"""
    return pytest.mark.requires_api(func)
