# 風險地圖報告 - 初始掃描

**文件編號**: RM-INIT-001  
**專案名稱**: AuraTrade - AI 驅動的智能投資分析系統  
**生成日期**: 2026-02-06  
**生成工具**: Sentinel Test Architect v1.0.0  
**掃描類型**: 初始化專案掃描

---

## 📊 執行摘要

### 整體風險評估

| 指標 | 數值 | 狀態 |
|-----|------|------|
| 總檔案數 | 54 (後端) + 24 (前端) | 🟡 |
| 測試覆蓋率 | ~5% (估算) | 🔴 **Critical** |
| 高風險檔案 | 8 個 | 🔴 **Critical** |
| 中風險檔案 | 12 個 | 🟠 High |
| 已測試檔案 | 2 個 | 🔴 **不足** |

### 關鍵發現

1. ⚠️ **Critical Services 完全未測試**
   - `AuthService` - 認證服務（安全核心）
   - `TechnicalIndicatorService` - 技術指標計算（財務邏輯）
   - `YahooFinanceService` - 外部 API 整合

2. ⚠️ **前端測試框架缺失**
   - 無 Vitest 配置
   - 無任何元件測試
   - 建議優先安裝測試依賴

3. ⚠️ **複雜業務邏輯未覆蓋**
   - 安全模組（密碼、Token）
   - 財務計算（技術指標、價格分析）
   - 外部服務整合

---

## 🔴 Critical 風險區域 (需立即處理)

### 1. 認證與安全模組

**檔案**: `backend/apps/core/security.py`  
**風險等級**: 🔴 **Critical**  
**複雜度評估**: High  
**當前覆蓋率**: 0%  
**目標覆蓋率**: ≥90%

**關鍵函數** (未測試):
- `hash_password()` - 密碼雜湊
- `verify_password()` - 密碼驗證
- `create_access_token()` - JWT Access Token 生成
- `create_refresh_token()` - Refresh Token 生成
- `decode_token()` - Token 解碼與驗證

**風險說明**:
- 認證是系統安全的核心，任何漏洞都可能導致嚴重後果
- JWT Token 處理錯誤可能導致未授權訪問
- 密碼處理邏輯必須經過嚴格測試

**建議測試案例**:
```python
# TC-UT-SEC-001: 密碼雜湊唯一性
def test_hash_password_unique()

# TC-UT-SEC-002: 密碼驗證正確性
def test_verify_password_correct()

# TC-UT-SEC-003: Token 過期處理
def test_token_expiration()

# TC-UT-SEC-004: 無效 Token 拒絕
def test_invalid_token_rejected()

# TC-UT-SEC-005: Token 數據完整性
def test_token_data_integrity()
```

---

### 2. AuthService 業務邏輯

**檔案**: `backend/apps/services/auth_service.py`  
**風險等級**: 🔴 **Critical**  
**複雜度評估**: High  
**當前覆蓋率**: 0%  
**目標覆蓋率**: ≥90%

**風險說明**:
- 註冊/登入邏輯是應用入口
- 錯誤處理不當可能導致資訊洩漏
- 需要測試各種邊界條件

**關鍵測試場景**:
- ✅ 正常註冊流程
- ❌ 重複email註冊
- ❌ 弱密碼拒絕
- ❌ SQL Injection 防護
- ❌ 登入失敗次數限制

---

### 3. TechnicalIndicatorService 財務計算

**檔案**: `backend/apps/core/services/technical_indicators.py`  
**風險等級**: 🔴 **Critical**  
**複雜度評估**: Very High  
**當前覆蓋率**: 0%  
**目標覆蓋率**: ≥90%

**關鍵函數**:
- `calculate_ma()` - 移動平均線
- `calculate_ema()` - 指數移動平均
- `calculate_macd()` - MACD 指標
- `calculate_rsi()` - RSI 指標（推測）

**風險說明**:
- 財務計算錯誤會直接影響投資決策
- 數值計算精度至關重要
- 邊界條件（空數據、極端值）需要覆蓋

**這個函數很勇敢，它假設輸入數據永遠是完美的，但我建議加上防彈測試！**

**建議測試案例**:
```python
# TC-UT-TI-001: MA 基本計算
def test_ma_calculation_accuracy()

# TC-UT-TI-002: 空數據處理
def test_ma_empty_data()

# TC-UT-TI-003: 不足週期數據
def test_ma_insufficient_data()

# TC-UT-TI-004: 極端值處理
def test_ma_extreme_values()

# TC-UT-TI-005: MACD 交叉信號
def test_macd_crossover_signal()
```

---

### 4. YahooFinanceService 外部 API

**檔案**: `backend/apps/core/services/yahoo_finance.py`  
**風險等級**: 🔴 **Critical**  
**複雜度評估**: High  
**當前覆蓋率**: 0%  
**目標覆蓋率**: ≥75%

**風險說明**:
- 外部 API 可能失敗、超時、返回錯誤數據
- 需要 Mock 外部請求進行測試
- 重試邏輯、錯誤處理需要驗證

**建議測試案例**:
```python
# TC-IT-YF-001: API 正常回應
@pytest.mark.integration
def test_fetch_stock_price_success()

# TC-UT-YF-002: API 超時處理
def test_api_timeout_handling()

# TC-UT-YF-003: 無效股票代碼
def test_invalid_stock_symbol()

# TC-UT-YF-004: API 限流處理
def test_rate_limit_handling()
```

---

## 🟠 High 風險區域

### 5. GeminiService AI 分析

**檔案**: `backend/apps/core/services/gemini_service.py`  
**風險等級**: 🟠 **High**  
**當前覆蓋率**: 0%  
**目標覆蓋率**: ≥75%

**風險說明**:
- AI API 呼叫成本高，需要 Mock
- Prompt 工程品質影響結果
- 需要測試異常處理

---

### 6. LineBotService 通知服務

**檔案**: `backend/apps/core/services/line_service.py`  
**風險等級**: 🟠 **High**  
**當前覆蓋率**: 0%  
**目標覆蓋率**: ≥60%

**關鍵函數**:
- `send_price_alert()`
- `send_news_alert()`
- `send_transaction_notification()`

---

### 7. GoogleNewsService 新聞爬蟲

**檔案**: `backend/apps/core/services/google_news_service.py`  
**風險等級**: 🟠 **High**  
**當前覆蓋率**: 0%  
**目標覆蓋率**: ≥60%

**風險說明**:
- 爬蟲可能因網站結構變更而失效
- 需要測試 HTML 解析邏輯

---

### 8. StockListManager 股票清單管理

**檔案**: `backend/apps/core/services/stock_list_manager.py`  
**風險等級**: 🟠 **High**  
**複雜度評估**: Medium-High  
**當前覆蓋率**: 0%

**關鍵函數**:
- `get_all_stocks()` - 獲取所有股票
- `search_stocks()` - 搜尋股票
- `_fetch_twse_stocks()` - 台股上市
- `_fetch_tpex_stocks()` - 台股上櫃

---

## 🟡 Medium 風險區域

### 9-12. 資料庫模型層

**檔案**:
- `backend/apps/models/user.py`
- `backend/apps/models/position.py`
- `backend/apps/models/ai_recommendation.py`
- `backend/apps/models/stock_news.py`

**風險等級**: 🟡 **Medium**  
**當前覆蓋率**: 0%  
**目標覆蓋率**: ≥60%

**風險說明**:
- ORM 模型邏輯相對簡單
- 主要測試關係、約束、驗證邏輯

---

## 🟢 低風險區域

### 前端元件

**當前狀態**: 無測試框架  
**優先級**: Medium (先完成後端 Critical 模組)

**關鍵元件** (未測試):
- `WatchlistCard.tsx` - 自選股卡片
- `StockChart.tsx` - 股價圖表
- `AlertModal.tsx` - 提醒設定
- `NotificationBell.tsx` - 通知鈴鐺

---

## 📈 測試缺口分析

### 按測試類型分類

| 測試類型 | 已有測試 | 缺失測試 | 優先級 |
|---------|---------|----------|--------|
| 單元測試 - 安全 | 0 | 5+ | 🔴 Critical |
| 單元測試 - 計算 | 0 | 10+ | 🔴 Critical |
| 單元測試 - 業務邏輯 | 0 | 15+ | 🟠 High |
| 整合測試 - API | 1 | 20+ | 🟠 High |
| 整合測試 - DB | 0 | 10+ | 🟡 Medium |
| E2E 測試 | 0 | 5+ | 🟡 Medium |
| 前端元件測試 | 0 | 20+ | 🟡 Medium |

---

## 🎯 建議行動計畫

### Phase 1: Critical 模組測試 (Week 1-2)

**優先級 P0** - 立即開始
1. ✅ **安全模組完整測試**
   - `security.py` - 所有函數
   - `AuthService` - 認證流程
   - 目標覆蓋率: 90%

2. ✅ **財務計算測試**
   - `TechnicalIndicatorService` - 所有指標
   - 重點：精度、邊界條件
   - 目標覆蓋率: 90%

**預估工時**: 16-20 小時  
**建議使用**: `Sentinel> generate-tests --module=security,technical_indicators`

---

### Phase 2: 外部服務整合測試 (Week 3)

**優先級 P1**
1. ✅ **Yahoo Finance Service**
   - Mock 外部 API
   - 錯誤處理測試
   - 目標覆蓋率: 75%

2. ✅ **Gemini Service**
   - Mock AI API
   - Prompt 測試
   - 目標覆蓋率: 75%

**預估工時**: 12-16 小時

---

### Phase 3: 業務邏輯與整合測試 (Week 4)

**優先級 P2**
1. ✅ **LINE 通知服務**
2. ✅ **新聞爬蟲服務**
3. ✅ **API 端點整合測試**

**預估工時**: 16-20 小時

---

### Phase 4: 前端測試建置 (Week 5)

**優先級 P3**
1. ✅ 安裝 Vitest + Testing Library
2. ✅ 核心元件測試
3. ✅ E2E 關鍵流程

**預估工時**: 20-24 小時

---

## 📊 風險矩陣

```
複雜度高 │   
        │   
        │  [security.py]      [technical_indicators.py]
        │      🔴                    🔴
        │  
        │  [yahoo_finance.py]   [auth_service.py]
        │      🔴                    🔴
        │  
        │  [gemini_service.py]  [line_service.py]
        │      🟠                    🟠
複雜度低 │  
        └───────────────────────────────────
          低覆蓋率 ←              → 高覆蓋率
```

**說明**:
- 🔴 Critical - 高複雜度 + 低覆蓋率 
→ **立即處理**
- 🟠 High - 中高複雜度 + 低覆蓋率 → 優先處理
- 🟡 Medium - 中等風險 → 規劃處理

---

## 🛠️ 建議使用 Sentinel 命令

### 快速生成測試
```bash
# 生成安全模組測試
Sentinel> generate-tests --file=backend/apps/core/security.py

# 生成技術指標測試
Sentinel> generate-tests --file=backend/apps/core/services/technical_indicators.py

# 生成 AuthService 測試
Sentinel> generate-tests --file=backend/apps/services/auth_service.py
```

### 自動生成 Mock
```bash
# 為外部 API 生成 Mock
Sentinel> generate-mocks --service=yahoo-finance,gemini
```

### 持續監控
```bash
# 完成初期測試後，使用快速測試
Sentinel> quick-test

# 定期產生新的風險地圖
Sentinel> risk-map
```

---

## 📝 結論

**整體評估**: 🔴 **High Risk**

AuraTrade 專案目前處於**高風險狀態**，核心業務邏輯幾乎完全未測試。

**關鍵發現**:
1. ⚠️ **安全模組零測試** - 這是最危險的狀況
2. ⚠️ **財務計算未驗證** - 直接影響投資決策準確性
3. ⚠️ **外部服務無容錯測試** - 可能導致運行時錯誤

**立即行動建議**:
1. 🔥 **本週完成**: `security.py` 與 `technical_indicators.py` 測試
2. 🔥 **下週完成**: `AuthService` 與 `YahooFinanceService` 測試
3. 📦 **安裝前端測試框架**: Vitest + Playwright

**使用 Sentinel 可以加速 70% 的測試生成時間！**

---

**報告生成時間**: 2026-02-06 18:30 UTC+8  
**下次掃描建議**: 完成 Phase 1 後 (約 2 週後)  
**負責人**: Sentinel Test Architect  
**配置檔**: `.sentinel-config.yaml`