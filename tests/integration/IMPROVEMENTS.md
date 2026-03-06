# 🎯 整合測試改進建議

**評估日期:** 2026-02-06  
**當前評分:** 82/100 (GOOD) 🟢  
**目標評分:** 95/100 (EXCELLENT)

---

## 📊 評估摘要

您的整合測試**已符合業界標準**，但仍有提升空間。以下是詳細的改進建議。

### 當前狀態
✅ **符合標準項目 (9/10):**
- 測試結構與組織 (95%)
- 測試隔離性 (90%)  
- Async 支持 (100%)
- Fixtures 設計 (85%)
- 測試覆蓋 (80%)
- 斷言充分性 (85%)
- 文檔完整性 (95%)

⚠️ **需改進項目 (3):**
- Mock 策略 (60%)
- 參數化測試 (40%)
- CI/CD 就緒度 (70%)

---

## 🚀 優先級改進建議

### Priority 1: Mock 外部依賴 (High Impact)

**當前問題:**
- 股票測試依賴真實 Yahoo Finance API
- 可能因網路或 API 限制失敗
- 執行時間較長

**改進方案:**

#### 1.1 添加 Mock Fixtures

```python
# tests/integration/conftest.py

@pytest.fixture
def mock_yahoo_finance(monkeypatch):
    """Mock Yahoo Finance API 回應"""
    
    class MockYahooService:
        async def get_quote(self, symbol: str):
            return {
                "symbol": symbol,
                "price": 500.0,
                "name": "Mock Stock",
                "change": 5.0,
                "changePercent": 1.0
            }
        
        async def get_history(self, symbol: str, period: str):
            return {
                "symbol": symbol,
                "history": [
                    {"date": "2024-01-01", "close": 495.0},
                    {"date": "2024-01-02", "close": 500.0}
                ]
            }
    
    # 替換真實服務
    from apps.core.services import yahoo_finance
    monkeypatch.setattr(
        yahoo_finance, 
        "YahooFinanceService", 
        lambda: MockYahooService()
    )
    
    return MockYahooService()


@pytest.fixture
def mock_gemini_ai(monkeypatch):
    """Mock Gemini AI 服務"""
    
    async def mock_analyze(*args, **kwargs):
        return {
            "sentiment": "positive",
            "score": 0.85,
            "confidence": 0.92
        }
    
    monkeypatch.setattr(
        "apps.core.services.gemini_service.GeminiService.analyze_news_sentiment",
        mock_analyze
    )
```

#### 1.2 使用 Mock 的測試

```python
# tests/integration/api/test_stock_integration.py

@pytest.mark.asyncio
@pytest.mark.integration
async def test_search_with_mock(
    self, 
    client: AsyncClient, 
    auth_headers: Dict[str, str],
    mock_yahoo_finance  # 使用 Mock
):
    """TC-INT-021: 搜尋台股 (使用 Mock)"""
    response = await client.get(
        "/api/v1/stocks/search",
        headers=auth_headers,
        params={"q": "2330"}
    )
    
    assert response.status_code == 200
    # Mock 確保可預測的結果
```

**預期收益:**
- ⚡ 執行速度提升 **70%**
- 🎯 測試穩定性提升 **90%**
- 🔒 避免外部 API 依賴

---

### Priority 2: 參數化測試 (Code Quality)

**當前問題:**
- 多個相似測試重複代碼
- 可維護性較低

**改進方案:**

#### 2.1 Email 驗證參數化

```python
# tests/integration/api/test_auth_integration.py

@pytest.mark.parametrize("invalid_email,expected_error", [
    ("not-an-email", "invalid email format"),
    ("@missing-local.com", "invalid email format"),
    ("missing-at.com", "invalid email format"),
    ("spaces in@email.com", "invalid email format"),
    ("", "email is required"),
])
@pytest.mark.asyncio
@pytest.mark.integration
async def test_register_invalid_emails(
    self, 
    client: AsyncClient, 
    invalid_email: str,
    expected_error: str
):
    """TC-INT-005: 多種無效 email 格式測試"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    
    user_data = {
        "email": invalid_email,
        "username": f"user_{timestamp}",
        "password": "ValidPass123!",
        "confirm_password": "ValidPass123!"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 422
    
    error = response.json()
    assert expected_error.lower() in str(error).lower()
```

#### 2.2 股票代碼參數化

```python
# tests/integration/api/test_stock_integration.py

@pytest.mark.parametrize("symbol,market", [
    ("2330.TW", "TW"),
    ("2317.TW", "TW"),
    ("AAPL", "US"),
    ("MSFT", "US"),
])
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.requires_api
async def test_get_multiple_stock_quotes(
    self,
    client: AsyncClient,
    auth_headers: Dict[str, str],
    symbol: str,
    market: str
):
    """TC-INT-026: 獲取多個股票報價"""
    response = await client.get(
        f"/api/v1/stocks/{symbol}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    quote = response.json()
    assert quote["symbol"] == symbol
```

**預期收益:**
- 📉 代碼行數減少 **30%**
- 🧪 測試案例增加 **50%**
- 🔧 更易維護

---

### Priority 3: 測試數據工廠 (Maintainability)

**當前問題:**
- 測試數據分散在各測試中
- 修改數據結構需要更新多處

**改進方案:**

#### 3.1 創建測試工廠

```python
# tests/factories.py

from datetime import datetime
from typing import Dict, Any

class TestDataFactory:
    """測試數據工廠"""
    
    @staticmethod
    def create_user_data(**overrides) -> Dict[str, Any]:
        """生成用戶註冊數據"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        
        default_data = {
            "email": f"user_{timestamp}@test.com",
            "username": f"user_{timestamp}",
            "password": "ValidPass123!",
            "confirm_password": "ValidPass123!"
        }
        
        return {**default_data, **overrides}
    
    @staticmethod
    def create_stock_data(symbol: str = None, **overrides) -> Dict[str, Any]:
        """生成股票數據"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        default_data = {
            "symbol": symbol or f"TEST{timestamp[:4]}.TW",
            "name": f"測試股票_{timestamp}",
            "market": "TW",
            "price": 100.0
        }
        
        return {**default_data, **overrides}
    
    @staticmethod
    def create_position_data(**overrides) -> Dict[str, Any]:
        """生成持倉數據"""
        default_data = {
            "quantity": 100,
            "average_cost": 150.0,
            "purchase_date": datetime.utcnow().isoformat()
        }
        
        return {**default_data, **overrides}
```

#### 3.2 使用工廠

```python
# tests/integration/api/test_auth_integration.py

from tests.factories import TestDataFactory

class TestUserRegistration:
    
    @pytest.mark.asyncio
    async def test_register_new_user(self, client: AsyncClient):
        """使用工廠簡化測試"""
        user_data = TestDataFactory.create_user_data()
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        # ... 其他斷言
```

**預期收益:**
- 🎯 測試代碼更簡潔
- 🔄 數據結構變更只需修改一處
- 📦 可重用性提升

---

### Priority 4: 增強錯誤訊息驗證 (Quality)

**當前問題:**
- 只驗證 HTTP 狀態碼
- 未驗證錯誤訊息內容

**改進方案:**

#### 4.1 詳細錯誤驗證

```python
@pytest.mark.asyncio
async def test_register_duplicate_email_detailed(
    self, 
    client: AsyncClient, 
    test_user
):
    """TC-INT-003: 重複 email - 詳細錯誤驗證"""
    duplicate_data = TestDataFactory.create_user_data(
        email=test_user["email"]  # 使用已存在的 email
    )
    
    response = await client.post("/api/v1/auth/register", json=duplicate_data)
    
    # 狀態碼驗證
    assert response.status_code in [400, 409]
    
    # 錯誤訊息驗證
    error = response.json()
    assert "detail" in error or "message" in error
    
    error_msg = str(error).lower()
    assert "email" in error_msg
    assert "already" in error_msg or "exists" in error_msg or "duplicate" in error_msg
    
    # 錯誤代碼驗證 (如果有)
    if "code" in error:
        assert error["code"] in ["EMAIL_EXISTS", "DUPLICATE_EMAIL"]
```

#### 4.2 驗證輔助函數

```python
# tests/helpers.py

def assert_error_response(
    response, 
    expected_status: int,
    error_keywords: list[str]
):
    """驗證錯誤回應的輔助函數"""
    assert response.status_code == expected_status
    
    error = response.json()
    error_str = str(error).lower()
    
    for keyword in error_keywords:
        assert keyword.lower() in error_str, \
            f"Expected '{keyword}' in error message"
```

**預期收益:**
- 🔍 更精確的錯誤定位
- 📝 更好的錯誤訊息文檔
- 🛡️ API 契約驗證

---

### Priority 5: CI/CD 整合 (DevOps)

**當前問題:**
- 需要手動環境設置
- 缺少自動化流程

**改進方案:**

#### 5.1 Docker Compose 測試環境

```yaml
# docker-compose.test.yml

version: '3.8'

services:
  test-db:
    image: postgres:15
    environment:
      POSTGRES_DB: auratrade_test
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5433:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
  
  test-runner:
    build:
      context: .
      dockerfile: Dockerfile.test
    depends_on:
      test-db:
        condition: service_healthy
    environment:
      TEST_DATABASE_URL: postgresql+asyncpg://postgres:postgres@test-db:5432/auratrade_test
      PYTHONPATH: /app/backend
    volumes:
      - ./backend:/app/backend
      - ./tests:/app/tests
    command: pytest tests/integration/ -v --cov
```

#### 5.2 GitHub Actions 工作流程

```yaml
# .github/workflows/integration-tests.yml

name: Integration Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: auratrade_test
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
      
      - name: Run Integration Tests
        env:
          TEST_DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/auratrade_test
          PYTHONPATH: ${{ github.workspace }}/backend
        run: |
          pytest tests/integration/ -v \
            --cov=backend/apps \
            --cov-report=xml \
            --cov-report=term-missing \
            --junitxml=reports/junit.xml
      
      - name: Upload Coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
      
      - name: Publish Test Results
        uses: EnricoMi/publish-unit-test-result-action@v2
        if: always()
        with:
          files: reports/junit.xml
```

**預期收益:**
- 🤖 自動化測試執行
- ⚡ PR 提交即時反饋
- 📊 覆蓋率追蹤

---

## 📈 實施路線圖

### Week 1: Mock & Parametrize (Quick Wins)
- [ ] Day 1-2: 添加外部 API Mock fixtures
- [ ] Day 3-4: 重構為參數化測試
- [ ] Day 5: 驗證改進效果

**預期收益:** 執行時間 -70%, 代碼行數 -30%

### Week 2: Testing Infrastructure
- [ ] Day 1-2: 創建測試數據工廠
- [ ] Day 3-4: 增強錯誤驗證
- [ ] Day 5: 更新文檔

**預期收益:** 可維護性 +50%, 測試質量 +30%

### Week 3: CI/CD Integration
- [ ] Day 1-2: Docker Compose 測試環境
- [ ] Day 3-4: GitHub Actions 設置
- [ ] Day 5: 優化工作流程

**預期收益:** 自動化 100%, 開發效率 +40%

---

## 🎯 改進後預期評分

| 評估項目 | 當前 | 改進後 | 提升 |
|---------|------|--------|------|
| Mock 策略 | 60% | **95%** | +35% |
| 參數化測試 | 40% | **90%** | +50% |
| CI/CD 就緒 | 70% | **95%** | +25% |
| **整體評分** | **82/100** | **95/100** | **+13** |

---

## 📝 快速改進檢查清單

### 本週可完成 ✅
- [x] 添加測試標記 (@pytest.mark.integration)
- [ ] 創建 Mock fixtures (yahoo_finance, gemini)
- [ ] 重構 3-5 個測試為參數化
- [ ] 創建基本測試工廠

### 下週目標 🎯
- [ ] 完成所有外部 API Mock
- [ ] 所有重複測試改為參數化
- [ ] 增強錯誤訊息驗證
- [ ] Docker Compose 設置

### 長期目標 🚀
- [ ] GitHub Actions CI/CD
- [ ] Codecov 整合
- [ ] 性能基準測試
- [ ] 測試覆蓋率 → 95%

---

## 💡 參考資源

### 文檔
- [pytest 參數化測試](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [pytest-asyncio 指南](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock 文檔](https://docs.python.org/3/library/unittest.mock.html)

### 最佳實踐
- [Google Testing Blog](https://testing.googleblog.com/)
- [Martin Fowler - Integration Testing](https://martinfowler.com/bliki/IntegrationTest.html)
- [pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)

---

**評估者:** Sentinel Test Architect  
**下次評估建議:** 實施改進後 (2 週後)  
**目標:** 達到 95/100 (EXCELLENT) 🏆
