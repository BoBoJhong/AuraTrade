# AuraTrade 測試套件

**專案:** AuraTrade - AI 驅動的智能投資分析系統  
**測試框架:** Vitest (Frontend), Pytest (Backend), Playwright (E2E)  
**管理工具:** Sentinel Test Architect v1.0.0  
**配置檔案:** `.sentinel-config.yaml` (專案根目錄)  
**最後更新:** 2026-02-06

> 🛡️ 本測試套件由 **Sentinel Agent** 管理與維護  
> 測試策略: 單元(60%) / 整合(30%) / E2E(10%)  
> 覆蓋率目標: Critical≥90% | High≥75% | Overall≥70%

---

## 📂 目錄結構

```
tests/
├── README.md                    # 本檔案 - 測試總覽與執行指引
├── unit/                        # 單元測試 (60%)
│   ├── services/                # 後端服務層測試
│   ├── components/              # 前端元件測試
│   └── utils/                   # 工具函數測試
├── integration/                 # 整合測試 (30%)
│   ├── api/                     # API 路由測試
│   └── database/                # 資料庫操作測試
├── e2e/                         # E2E 測試 (10%)
│   ├── scenarios/               # 測試場景 (Playwright)
│   ├── fixtures/                # 測試數據與 Fixtures
│   ├── screenshots/             # 失敗截圖 (gitignored)
│   └── videos/                  # 測試錄影 (gitignored)
├── reports/                     # 測試報告 (Sentinel 自動產出)
│   ├── test-plans/              # 測試計畫 (TP-YYYYMMDD-SEQ.md)
│   ├── test-reports/            # 詳細測試報告 (TR-YYYYMMDD-SEQ.md)
│   ├── risk-maps/               # 風險地圖 (RM-YYYYMMDD-SEQ.md)
│   └── quality-reports/         # 品質趨勢報告 (QR-YYYYMMDD-SEQ.md)
└── mocks/                       # Mock 數據與配置
    ├── api-responses/           # API Mock 回應
    └── database-seeds/          # 測試資料庫 Seed 數據
```

---

## 🚀 快速開始

### 1. 安裝測試依賴

```bash
# 後端 (Pytest 已安裝)
cd backend
pip install pytest pytest-asyncio pytest-cov pytest-httpx

# 前端 (需要安裝 Vitest)
cd frontend
npm install --save-dev vitest @vitest/ui jsdom
npm install --save-dev @testing-library/react @testing-library/jest-dom
npm install --save-dev @testing-library/user-event

# E2E (Playwright)
npm install --save-dev @playwright/test
npx playwright install
```

### 2. 執行測試

```bash
# 後端單元測試
cd backend
pytest tests/unit -v

# 前端單元測試
cd frontend
npm run test

# E2E 測試
npm run test:e2e

# 完整測試 (所有層級)
npm run test:all
```

### 3. 查看覆蓋率報告

```bash
# 後端覆蓋率
pytest --cov=apps --cov-report=html
# 報告位置: tests/reports/htmlcov/index.html

# 前端覆蓋率
npm run test:coverage
# 報告位置: tests/reports/coverage-frontend/index.html
```

---

## 🛡️ 使用 Sentinel Agent

### 基本命令

```bash
# 初始化 (已完成)
Sentinel> init

# 掃描專案並識別測試需求
Sentinel> scan-project

# 自動生成測試案例
Sentinel> generate-tests

# 快速測試 (只測變更檔案)
Sentinel> quick-test

# 產生風險地圖
Sentinel> risk-map

# 執行完整測試週期
Sentinel> full-test-cycle

# 生成品質報告
Sentinel> quality-report
```

### Sentinel 功能說明

| 功能 | 命令 | 說明 |
|------|------|------|
| 專案掃描 | `SC` | 分析代碼複雜度，識別測試缺口 |
| 測試生成 | `GT` | 自動生成單元/整合/E2E 測試 |
| 快速測試 | `QT` | 增量測試，省時 60-90% |
| 風險地圖 | `RM` | 標記高風險低覆蓋率區域 |
| Mock 生成 | `GM` | 自動生成測試數據與 Mock |
| 測試策略 | `TS` | AI 建議測試優先級 |
| 失敗修復 | `FP` | 分析失敗測試並提供修復建議 |
| TDD 模式 | `TD` | 先寫測試後實現的輔助工具 |
| 品質報告 | `QR` | 完整的品質趨勢與技術債務分析 |
| 完整週期 | `FC` | 一鍵執行完整測試流程 |

---

## 🎯 測試策略

### 測試金字塔

```
        E2E (10%)          ← Playwright (關鍵使用者流程)
       ▲▲▲▲▲▲▲▲▲
      ▲▲▲▲▲▲▲▲▲▲▲
     整合測試 (30%)        ← Pytest / Vitest (API / DB)
    ▲▲▲▲▲▲▲▲▲▲▲▲▲▲
   ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
  單元測試 (60%)          ← Pytest / Vitest (函數 / 元件)
 ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
```

### 優先測試模組 (依風險等級)

#### 🔴 Critical (目標覆蓋率 ≥90%)
- `AuthService` - 認證安全核心
- `TechnicalIndicatorService` - 財務計算邏輯

#### 🟠 High (目標覆蓋率 ≥75%)
- `YahooFinanceService` - 外部 API 整合
- `GeminiService` - AI 分析核心

#### 🟡 Medium (目標覆蓋率 ≥60%)
- `LineBotService` - 通知服務
- `GoogleNewsService` - 新聞爬蟲

---

## 📊 覆蓋率目標

| 模組等級 | 目標覆蓋率 | 說明 |
|---------|-----------|------|
| Critical | ≥ 90% | 核心業務邏輯，不容失誤 |
| High | ≥ 75% | 重要功能，需高度保障 |
| Medium | ≥ 60% | 一般功能，基本測試 |
| **整體** | **≥ 70%** | **專案整體目標** |

---

## 🧪 測試類型說明

###  單元測試 (Unit Tests)
- **目標**: 測試單一函數/類別的邏輯正確性
- **特點**: 快速、獨立、Mock 外部依賴
- **位置**: `tests/unit/`
- **範例**: 測試技術指標計算、表單驗證邏輯

### 整合測試 (Integration Tests)
- **目標**: 測試模組間協作與外部服務整合
- **特點**: 涉及真實資料庫/API 呼叫
- **位置**: `tests/integration/`
- **範例**: API 端點測試、資料庫 CRUD 操作

### E2E 測試 (End-to-End Tests)
- **目標**: 測試完整使用者流程
- **特點**: 模擬真實用戶操作，跨瀏覽器
- **位置**: `tests/e2e/scenarios/`
- **範例**: 登入→查股票→設提醒→收到通知

---

## 📋 測試命名規範

### 測試檔案命名
- 單元測試: `test_{module_name}.py` / `{ComponentName}.test.tsx`
- 整合測試: `test_{feature}_{integration}.py`
- E2E 測試: `{user_flow}.spec.ts`

### 測試案例 ID
格式: `{type}-{module}-{seq:03d}`

範例:
- `TC-UT-AUTH-001` - 單元測試 (Unit Test) / Auth 模組 / 編號 001
- `TC-IT-API-015` - 整合測試 (Integration Test) / API 模組 / 編號 015
- `TC-E2E-LOGIN-001` - E2E 測試 / 登入流程 / 編號 001

---

## 🔧 測試配置檔案

### 後端 (Pytest)
- **配置檔**: `backend/pytest.ini`
- **覆蓋率**: `--cov=apps --cov-report=html`
- **標記**: `@pytest.mark.unit` / `@pytest.mark.integration`

### 前端 (Vitest)
- **配置檔**: `frontend/vitest.config.ts`
- **環境**: jsdom
- **別名**: `@/` → `src/`

### E2E (Playwright)
- **配置檔**: `frontend/playwright.config.ts`
- **瀏覽器**: Chromium, Firefox, WebKit
- **截圖**: 自動保存失敗截圖至 `tests/e2e/screenshots/`

---

## 📝 測試報告

### 自動產出報告 (by Sentinel)

1. **測試計畫** (`TP-YYYYMMDD-SEQ.md`)
   - 測試範圍與策略
   - 風險識別
   - 資源分配

2. **測試報告** (`TR-YYYYMMDD-SEQ.md`)
   - 詳細測試結果
   - 覆蓋率分析
   - 失敗案例分析

3. **風險地圖** (`RM-YYYYMMDD-SEQ.md`)
   - 高複雜度低覆蓋率區域
   - 優先改善建議

4. **品質報告** (`QR-YYYYMMDD-SEQ.md`)
   - 品質趨勢分析
   - 技術債務追蹤
   - ROI 計算

---

## 🚨 常見問題

### Q: 如何只執行特定標記的測試？
```bash
# Pytest
pytest -m unit              # 只跑單元測試
pytest -m "not slow"        # 跳過慢速測試
pytest -m critical          # 只跑關鍵測試

# Vitest
npm run test -- --run       # 單次執行不監聽
```

### Q: 測試失敗如何快速定位？
使用 Sentinel 的失敗修復功能：
```bash
Sentinel> fix-proposal
```

### Q: 如何提高測試速度？
1. 使用 `Sentinel> quick-test` 增量測試
2. 並行執行: `pytest -n auto`
3. 只跑變更相關測試

### Q: Mock 數據如何管理？
```bash
Sentinel> generate-mocks
```
自動掃描 API 定義並生成合理的 Mock 數據

---

## 📚 相關文檔

- [Sentinel Agent 使用指南](_bmad/_memory/sentinel-sidecar/QUICK_START.md)
- [測試最佳實踐](_bmad/_memory/sentinel-sidecar/knowledge/best-practices.md)
- [框架參考手冊](_bmad/_memory/sentinel-sidecar/knowledge/framework-references.md)
- [風險識別模式](_bmad/_memory/sentinel-sidecar/risk-patterns.md)

---

**維護者**: Sentinel Test Architect  
**建立日期**: 2026-02-06  
**版本**: 1.0.0 (Sentinel Managed)
````
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio

# E2E (Playwright)
npx playwright install
```

### 執行測試

#### 全部測試
```bash
npm run test:all        # 執行所有測試 (單元 + 整合 + E2E)
```

#### 單元測試
```bash
npm run test:unit       # 執行單元測試
npm run test:unit:watch # Watch 模式
npm run test:unit:cov   # 生成覆蓋率報告
```

#### 整合測試
```bash
npm run test:integration       # 執行整合測試
npm run test:integration:cov   # 生成覆蓋率報告
```

#### E2E 測試
```bash
npm run test:e2e               # 執行 E2E 測試
npm run test:e2e:headed        # 顯示瀏覽器執行
npm run test:e2e:debug         # 除錯模式
```

#### 特定測試
```bash
npm test -- payment.test.ts          # 執行特定檔案
npm test -- --testNamePattern="登入"  # 執行特定名稱的測試
```

---

## 📋 測試策略

### 測試金字塔分配
```
         /\
        /  \  E2E (10%)
       /----\  ~8 scenarios
      /      \
     / 整合測試 \ (30%)
    /----------\  ~45 tests
   /            \
  /   單元測試    \ (60%)
 /----------------\  ~150 tests
```

### 覆蓋率目標
- **核心業務邏輯:** 90%+ (payment, trading, auth)
- **一般功能:** 80%+
- **工具函數:** 85%+
- **整體目標:** 85%+

### 優先級定義
| 優先級 | 標籤 | 測試時機 | 範例 |
|-------|------|---------|------|
| **P0** | Critical | 每次 commit | 登入、支付、交易核心流程 |
| **P1** | High | 每次 PR merge | 資料驗證、權限檢查 |
| **P2** | Medium | 每日定時 | UI 排版、非關鍵功能 |
| **P3** | Low | 每週定時 | 效能測試、跨瀏覽器相容性 |

---

## 🛡️ 使用 Sentinel Agent

Sentinel 是專為本專案設計的測試自動化專家,可協助:

### 可用命令

| 命令 | 功能 | 輸出 |
|------|------|------|
| `[FC]` | 執行完整測試週期 | TP + 測試檔案 + TR |
| `[SC]` | 掃描專案代碼 | 終端輸出分析結果 |
| `[RM]` | 產生風險地圖 | `reports/risk-maps/RM-{date}-{seq}.md` |
| `[GT]` | 自動生成測試 | `unit/` 或 `integration/` 下的測試檔案 |
| `[GM]` | 生成 Mock 資料 | `mocks/` 下的 Mock 檔案 |
| `[TS]` | 建議測試策略 | 終端輸出策略建議 |
| `[FP]` | 修復失敗測試 | 終端輸出修復建議 |
| `[TD]` | TDD 模式 | 測試骨架 + 空函數 |
| `[QR]` | 品質報告 | `reports/quality-reports/QR-{date}-{seq}.md` |

### 使用範例

#### 完整測試週期
```
開發者: *full-cycle --scope=src/features/trading

Sentinel:
  🛡️ 開始完整測試週期 (範圍: trading 模組)
  
  [1/5] 測試計畫生成中...
  ✅ 產出: tests/reports/test-plans/TP-20260206-001.md
  
  [2/5] 單元測試執行中...
  ✅ 生成 45 個測試案例
  
  [3/5] 整合測試執行中...
  ✅ 測試 5 個 API endpoints
  
  [4/5] E2E 測試執行中...
  ✅ 3 個關鍵場景全部通過
  
  [5/5] 測試報告生成中...
  ✅ 產出: tests/reports/test-reports/TR-20260206-001.md
```

#### 產生風險地圖
```
開發者: *risk-map

Sentinel:
  🛡️ 掃描專案代碼風險...
  
  ✅ 掃描完成
  📊 發現 8 個風險區域:
     - 🔴 Critical: 2 個
     - 🟡 High: 3 個
     - 🟢 Medium: 3 個
  
  📄 風險地圖已生成: tests/reports/risk-maps/RM-20260206-001.md
```

---

## 📊 追溯性編號系統

### 文件類型代碼

| 代碼 | 類型 | 格式 | 範例 | 位置 |
|------|------|------|------|------|
| **TP** | 測試計畫 | TP-YYYYMMDD-SEQ | TP-20260206-001.md | reports/test-plans/ |
| **TR** | 測試報告 | TR-YYYYMMDD-SEQ | TR-20260206-001.md | reports/test-reports/ |
| **RM** | 風險地圖 | RM-YYYYMMDD-SEQ | RM-20260206-001.md | reports/risk-maps/ |
| **QR** | 品質報告 | QR-YYYYMMDD-SEQ | QR-20260206-001.md | reports/quality-reports/ |
| **TC** | 測試案例 | TC-{LEVEL}-{MODULE}-SEQ | TC-UT-PAYMENT-001 | (測試檔案內) |

### 追溯範例

```
TP-20260206-001 (測試計畫)
  └── 規劃測試案例:
      ├── TC-UT-PAYMENT-001
      ├── TC-UT-PAYMENT-002
      ├── TC-IT-API-010
      └── TC-E2E-TRADING-001
  └── 產出報告:
      └── TR-20260206-001 (測試報告)
          └── 執行結果:
              ├── TC-UT-PAYMENT-001: PASS ✅
              ├── TC-UT-PAYMENT-002: FAIL ❌
              ├── TC-IT-API-010: PASS ✅
              └── TC-E2E-TRADING-001: PASS ✅
```

---

## 🔍 查看測試報告

### 最新報告
```bash
# 測試計畫
cat tests/reports/test-plans/TP-$(date +%Y%m%d)-*.md | tail -1

# 測試報告
cat tests/reports/test-reports/TR-$(date +%Y%m%d)-*.md | tail -1

# 風險地圖
cat tests/reports/risk-maps/RM-$(date +%Y%m%d)-*.md | tail -1
```

### HTML 報告
```bash
# 覆蓋率報告
open tests/unit/coverage/lcov-report/index.html

# Playwright 報告
npx playwright show-report
```

---

## 🛠️ 維護指南

### 新增測試

#### 1. 單元測試
```typescript
// tests/unit/services/payment.test.ts
import { calculateDiscount } from '@/services/payment';

describe('Payment Service', () => {
  describe('calculateDiscount', () => {
    it('should calculate correct discount', () => {
      expect(calculateDiscount(1000, 0.2)).toBe(800);
    });
    
    it('should reject negative price', () => {
      expect(() => calculateDiscount(-100, 0.2)).toThrow();
    });
  });
});
```

#### 2. 整合測試
```typescript
// tests/integration/api/user-routes.test.ts
import request from 'supertest';
import { app } from '@/app';

describe('User API', () => {
  it('POST /api/users should create user', async () => {
    await request(app)
      .post('/api/users')
      .send({ name: 'Test', email: 'test@example.com' })
      .expect(201);
  });
});
```

#### 3. E2E 測試
```typescript
// tests/e2e/scenarios/login-flow.spec.ts
import { test, expect } from '@playwright/test';

test('user should be able to login', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[data-testid="email"]', 'test@example.com');
  await page.fill('[data-testid="password"]', 'password123');
  await page.click('[data-testid="login-button"]');
  await expect(page).toHaveURL('/dashboard');
});
```

### 報告封存
```bash
# 封存 30 天前的報告
node scripts/archive-reports.js --days=30
```

---

## 📞 常見問題

### Q: 測試失敗時如何除錯?
```bash
# 1. 查看詳細錯誤訊息
npm test -- --verbose

# 2. 執行單一測試
npm test -- payment.test.ts

# 3. 使用 Sentinel 修復建議
開發者: *fix-proposal
```

### Q: 如何提高測試覆蓋率?
```bash
# 1. 查看覆蓋率報告
npm run test:unit:cov
open tests/unit/coverage/lcov-report/index.html

# 2. 使用 Sentinel 產生風險地圖
開發者: *risk-map

# 3. 針對低覆蓋率檔案補充測試
開發者: *generate-tests --file=src/services/payment.ts
```

### Q: E2E 測試太慢怎麼辦?
```bash
# 1. 平行執行
npx playwright test --workers=4

# 2. 只跑關鍵場景 (tagged tests)
npx playwright test --grep=@critical

# 3. 使用 Headless 模式 (預設)
npm run test:e2e
```

---

## 📈 持續整合 (CI/CD)

### GitHub Actions 整合
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run unit tests
        run: npm run test:unit:cov
      
      - name: Run integration tests
        run: npm run test:integration:cov
      
      - name: Run E2E tests
        run: npm run test:e2e
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./tests/unit/coverage/lcov.info
      
      - name: Upload test reports
        uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: tests/reports/
```

---

## 📚 參考資源

- **測試金字塔理論:** `_bmad/_memory/sentinel-sidecar/knowledge/testing-pyramid.md`
- **框架參考文件:** `_bmad/_memory/sentinel-sidecar/knowledge/framework-references.md`
- **最佳實踐:** `_bmad/_memory/sentinel-sidecar/knowledge/best-practices.md`
- **完整測試週期:** `_bmad/_memory/sentinel-sidecar/workflows/full-test-cycle.md`
- **輸出結構規範:** `_bmad/_memory/sentinel-sidecar/workflows/test-output-structure.md`

---

## 👥 團隊協作

### 測試責任
- **開發者:** 編寫單元測試 (功能完成當下)
- **QA:** 設計整合測試與 E2E 場景
- **Sentinel Agent:** 自動生成測試骨架、風險識別、報告產出

### Code Review 檢查清單
- [ ] 新功能包含對應測試 (至少單元測試)
- [ ] 高風險區域達到 90%+ 覆蓋率
- [ ] 測試命名清晰描述行為
- [ ] 無測試實作細節 (測試使用者可見行為)
- [ ] 測試間相互獨立 (無順序依賴)

---

**維護者:** Development Team  
**Sentinel Agent 版本:** 1.0.0  
**文件版本:** 1.0.0  
**最後更新:** 2026-02-06
