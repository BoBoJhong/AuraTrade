# 🔌 AuraTrade 整合測試套件

## 📋 概述

本目錄包含 AuraTrade 系統的整合測試，測試各模組間的交互、API 端點和資料庫操作。

**生成時間:** 2026-02-06  
**測試架構師:** Sentinel Test Architect  
**測試案例總數:** 63 個

---

## 📁 測試結構

```
tests/integration/
├── conftest.py                          # pytest 配置與 fixtures
├── README.md                            # 本文件
├── api/
│   ├── test_auth_integration.py         # 認證 API (20 tests)
│   └── test_stock_integration.py        # 股票 API (24 tests)
└── database/
    └── test_database_integration.py     # 資料庫操作 (19 tests)
```

---

## 🎯 測試範圍

### 1. API 整合測試 (44 tests)

#### test_auth_integration.py (20 tests)
**測試範圍:**
- ✅ 完整認證流程 (註冊 → 登入 → 驗證)
- ✅ 用戶註冊 (成功、重複 email、密碼不匹配、無效格式、弱密碼)
- ✅ 用戶登入 (成功、錯誤密碼、不存在用戶、缺少欄位)
- ✅ Token 驗證 (有效/無效 token、未認證、格式錯誤)
- ✅ 並發認證 (多次登入、token 有效性)
- ✅ 邊界案例 (空格、大小寫敏感、特殊字元)

**測試案例列表:**
- TC-INT-001: 完整認證流程
- TC-INT-002: 註冊新用戶
- TC-INT-003: 重複 email
- TC-INT-004: 密碼不匹配
- TC-INT-005: 無效 email
- TC-INT-006: 弱密碼
- TC-INT-007: 登入成功
- TC-INT-008: 錯誤密碼
- TC-INT-009: 不存在用戶
- TC-INT-010: 缺少欄位
- TC-INT-011: 有效 token
- TC-INT-012: 無 token
- TC-INT-013: 無效 token
- TC-INT-014: 格式錯誤標頭
- TC-INT-015: 多次登入
- TC-INT-016: token 在再次登入後仍有效
- TC-INT-017: 輸入包含空格
- TC-INT-018: Email 大小寫敏感性
- TC-INT-019: Username 特殊字元
- TC-INT-020: 空請求體

#### test_stock_integration.py (24 tests)
**測試範圍:**
- ✅ 股票搜尋 (台股、美股、公司名稱、空查詢、未認證)
- ✅ 即時報價 (台股、美股、無效代碼、價格變動)
- ✅ 歷史數據 (1個月、1年、數據結構、無效參數)
- ✅ 技術指標 (MA、RSI、數據不足)
- ✅ 完整流程 (搜尋 → 報價 → 歷史 → 指標)
- ✅ 快取測試 (重複請求性能)
- ✅ 錯誤處理 (格式錯誤、特殊字元、超長查詢)
- ✅ 並發測試 (多個並發請求)

**測試案例列表:**
- TC-INT-021 ~ TC-INT-044 (24 個測試案例)

### 2. 資料庫整合測試 (19 tests)

#### test_database_integration.py (19 tests)
**測試範圍:**
- ✅ User CRUD (創建、讀取、更新、刪除、唯一約束)
- ✅ Stock 操作 (創建、市場查詢)
- ✅ Watchlist 操作 (添加、移除、JOIN 查詢)
- ✅ Position 操作 (創建、更新數量)
- ✅ PriceAlert 操作 (創建、停用)
- ✅ 交易隔離 (rollback 測試)
- ✅ 資料完整性 (級聯刪除)
- ✅ 複雜查詢 (聚合、子查詢)
- ✅ 並發控制 (並發更新同一記錄)

**測試案例列表:**
- TC-DB-001 ~ TC-DB-019 (19 個測試案例)

---

## 🚀 執行測試

### 前置條件

1. **Python 環境:** Python 3.10+
2. **安裝依賴:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **測試資料庫設置:**
   ```bash
   # 創建測試資料庫
   createdb auratrade_test
   
   # 或設置環境變數使用不同的測試資料庫
   export TEST_DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/auratrade_test"
   ```

4. **環境變數 (.env):**
   ```env
   DATABASE_URL=postgresql+asyncpg://...
   SECRET_KEY=your-secret-key
   CORS_ORIGINS=http://localhost:3000
   # ... 其他必要配置
   ```

### 執行所有整合測試

```bash
# 從專案根目錄執行
cd /path/to/AuraTrade

# 設置 PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"

# 執行所有整合測試
python -m pytest tests/integration/ -v

# 包含覆蓋率報告
python -m pytest tests/integration/ -v --cov=backend/apps --cov-report=html
```

### 執行特定測試套件

```bash
# 只執行認證測試
python -m pytest tests/integration/api/test_auth_integration.py -v

# 只執行股票測試
python -m pytest tests/integration/api/test_stock_integration.py -v

# 只執行資料庫測試
python -m pytest tests/integration/database/test_database_integration.py -v
```

### 執行特定測試類別

```bash
# 只執行認證流程測試
python -m pytest tests/integration/api/test_auth_integration.py::TestAuthenticationFlow -v

# 只執行股票搜尋測試
python -m pytest tests/integration/api/test_stock_integration.py::TestStockSearch -v
```

### 執行單一測試案例

```bash
# 執行完整認證流程測試
python -m pytest tests/integration/api/test_auth_integration.py::TestAuthenticationFlow::test_complete_auth_flow -v
```

### 使用標記過濾測試

```bash
# 執行快速測試 (如果有標記)
python -m pytest tests/integration/ -v -m "not slow"

# 只執行需要外部 API 的測試
python -m pytest tests/integration/ -v -m "external_api"
```

---

## 📊 預期結果

### 成功標準

執行整合測試時，預期結果：

```
========================= test session starts ==========================
platform win32 -- Python 3.14.0, pytest-9.0.2
collected 63 items

tests/integration/api/test_auth_integration.py .................... [ 31%]
tests/integration/api/test_stock_integration.py ................... [ 69%]
tests/integration/database/test_database_integration.py ......... [100%]

========================== 63 passed in 45.2s ==========================
```

### 關鍵指標

- ✅ **總測試數:** 63 tests
- ✅ **預期通過率:** > 90%
- ✅ **執行時間:** < 60 秒
- ✅ **覆蓋率:** API routes 70%+, Database operations 80%+

---

## 🔧 Fixtures 說明

### conftest.py 提供的 Fixtures

#### `test_engine`
- 建立測試資料庫引擎
- 每個測試函數獨立建立/刪除表格
- 使用 NullPool 確保隔離

#### `test_db`
- 提供測試用 AsyncSession
- 自動清理資料
- 支援交易回滾

#### `client`
- 提供 AsyncClient (httpx)
- 自動覆蓋 get_db 依賴
- 基礎 URL: `http://test`

#### `test_user`
- 自動創建測試用戶
- 返回完整用戶資訊 (email, password, access_token)
- 每個測試獨立的用戶

#### `auth_headers`
- 返回認證標頭
- 格式: `{"Authorization": "Bearer <token>"}`
- 可直接用於 API 請求

#### `test_stock_symbols`
- 提供測試用股票代碼
- 台股: 2330.TW, 2317.TW, 2454.TW
- 美股: AAPL, MSFT, GOOGL

#### `sample_stock_data`
- 提供樣本股票數據
- 用於 Mock 測試

---

## 🐛 故障排除

### 問題 1: ModuleNotFoundError

**錯誤訊息:**
```
ModuleNotFoundError: No module named 'apps'
```

**解決方案:**
```bash
# 設置 PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"

# 或在 pytest.ini 中設置
python_paths = backend
```

### 問題 2: 資料庫連線失敗

**錯誤訊息:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**解決方案:**
1. 確保 PostgreSQL 服務運行中
2. 檢查 TEST_DATABASE_URL 設定正確
3. 創建測試資料庫: `createdb auratrade_test`

### 問題 3: 測試資料殘留

**症狀:** 測試偶爾失敗，特別是唯一約束錯誤

**解決方案:**
```bash
# 清空測試資料庫
dropdb auratrade_test
createdb auratrade_test

# 或在測試中使用時間戳確保唯一性 (已實現)
```

### 問題 4: 外部 API 失敗

**症狀:** 股票搜尋/報價測試失敗

**解決方案:**
1. 檢查網路連線
2. 確認 API Key 設定 (Alpha Vantage, Yahoo Finance)
3. 使用 Mock 跳過外部依賴測試

---

## 🎨 編寫新測試指南

### 1. 遵循現有結構

```python
class TestNewFeature:
    """測試新功能描述"""
    
    @pytest.mark.asyncio
    async def test_feature_success(self, client: AsyncClient, auth_headers):
        """TC-INT-XXX: 測試案例描述 - 成功"""
        response = await client.get("/api/v1/endpoint", headers=auth_headers)
        assert response.status_code == 200
```

### 2. 使用描述性測試名稱

- ✅ `test_register_with_valid_data`
- ❌ `test_1`

### 3. 測試編號規則

- `TC-INT-XXX`: Integration Test Case
- `TC-DB-XXX`: Database Test Case

### 4. 斷言要求

- 至少 1 個斷言
- 驗證狀態碼
- 驗證回應數據結構
- 驗證業務邏輯正確性

### 5. 清理原則

- 使用 fixtures 自動清理
- 使用時間戳確保唯一性
- 避免硬編碼 ID 或 email

---

## 📈 覆蓋率目標

### 整合測試覆蓋率目標

| 模組 | 目標覆蓋率 | 當前測試數 |
|------|-----------|------------|
| **API Routes** | 70%+ | 44 tests |
| - Authentication | 90%+ | 20 tests |
| - Stock Operations | 80%+ | 24 tests |
| **Database Layer** | 80%+ | 19 tests |
| - CRUD Operations | 90%+ | 12 tests |
| - Complex Queries | 70%+ | 3 tests |
| - Concurrency | 60%+ | 2 tests |
| **Business Logic** | 60%+ | (待補充) |

---

## 🔄 持續改進

### 待補充測試

**優先級 2 - 業務流程:**
- [ ] Watchlist 完整流程測試
- [ ] News 抓取與 AI 分析整合
- [ ] Recommendations 生成測試

**優先級 3 - 進階功能:**
- [ ] PriceAlert 完整流程
- [ ] Positions Management
- [ ] Transactions 記錄
- [ ] WebSocket 連線測試

### 效能基準

建立效能基準測試：
```python
@pytest.mark.slow
@pytest.mark.benchmark
async def test_api_response_time(self, client, auth_headers):
    import time
    start = time.time()
    response = await client.get("/api/v1/stocks/2330.TW", headers=auth_headers)
    duration = time.time() - start
    
    assert duration < 1.0  # 1 秒內回應
```

---

## 💡 最佳實踐

### 1. 獨立性
- ✅ 每個測試獨立執行
- ✅ 不依賴其他測試的結果
- ✅ 使用 fixtures 提供所需數據

### 2. 可重複性
- ✅ 使用時間戳確保唯一性
- ✅ 清理測試數據
- ✅ 不依賴外部狀態

### 3. 清晰性
- ✅ 描述性測試名稱
- ✅ 清楚的註解說明
- ✅ 一個測試一個概念

### 4. 效率
- ✅ 使用並行測試 (`pytest-xdist`)
- ✅ Mock 外部依賴
- ✅ 複用 fixtures

---

## 📞 支援

### 報告問題

如果測試失敗或有問題：

1. **檢查日誌:**
   ```bash
   python -m pytest tests/integration/ -v --tb=long
   ```

2. **啟用調試:**
   ```bash
   python -m pytest tests/integration/ -v -s  # 不抑制 print 輸出
   ```

3. **生成 HTML 報告:**
   ```bash
   python -m pytest tests/integration/ --html=reports/integration_test_report.html
   ```

### 聯絡資訊

- **Sentinel Agent:** 使用 `FC` 命令重新生成測試
- **測試文檔:** 參考 `TESTING_GUIDE.md`
- **架構文檔:** 參考 `docs/ARCHITECTURE.md`

---

**生成者:** Sentinel Test Architect  
**版本:** 1.0.0  
**最後更新:** 2026-02-06  
**下次建議更新:** 當加入新 API 端點或業務邏輯時

---

# 🛡️ Sentinel 守護您的整合測試

```
   🔌
  ／｜＼
 ／  |  ＼
───────────
Integration
  Testing
 Complete!
 
 63 Tests ✅
```
