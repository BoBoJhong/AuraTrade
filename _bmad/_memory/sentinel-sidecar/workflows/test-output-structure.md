# 測試輸出結構規範 (Test Output Structure)

**目標：** 定義清晰的測試檔案組織結構與追溯性編號系統

---

## 標準目錄結構

```
{project-root}/tests/
├── README.md                          # 測試總覽與執行指引
├── unit/                              # 單元測試
│   ├── services/                      # 按模組分類
│   │   ├── payment.test.ts
│   │   └── auth.test.ts
│   ├── utils/
│   │   ├── calculator.test.ts
│   │   └── formatter.test.ts
│   └── coverage/                      # 覆蓋率報告
│       └── lcov-report/
├── integration/                       # 整合測試
│   ├── api/
│   │   ├── user-routes.test.ts
│   │   └── order-routes.test.ts
│   ├── database/
│   │   └── user-repository.test.ts
│   └── coverage/
├── e2e/                               # E2E 測試
│   ├── scenarios/
│   │   ├── checkout-flow.spec.ts
│   │   └── login-flow.spec.ts
│   ├── fixtures/                      # 測試數據
│   │   └── users.json
│   ├── screenshots/                   # 失敗截圖
│   └── videos/                        # 測試錄影
├── reports/                           # 測試報告 (Sentinel 產出)
│   ├── test-plans/                    # 測試計畫
│   │   ├── TP-20260206-001.md
│   │   └── TP-20260206-002.md
│   ├── test-reports/                  # 測試結果報告
│   │   ├── TR-20260206-001.md
│   │   ├── TR-20260206-001.html
│   │   └── TR-20260206-002.md
│   ├── risk-maps/                     # 風險地圖
│   │   ├── RM-20260206-001.md
│   │   └── RM-20260206-001.json       # 機器可讀格式
│   ├── quality-reports/               # 品質報告
│   │   ├── QR-20260206-001.md
│   │   └── QR-20260206-001.html
│   └── archives/                      # 歷史報告封存
│       └── 2026-01/
└── mocks/                             # Mock 數據與配置
    ├── api-responses/
    │   └── users.mock.json
    └── database-seeds/
        └── test-data.sql
```

---

## 追溯性編號系統

### 文件類型代碼

| 代碼 | 類型 | 範例 | 描述 |
|------|------|------|------|
| **TP** | Test Plan | TP-20260206-001 | 測試計畫 |
| **TR** | Test Report | TR-20260206-001 | 測試結果報告 |
| **RM** | Risk Map | RM-20260206-001 | 風險地圖 |
| **QR** | Quality Report | QR-20260206-001 | 品質報告 |
| **TC** | Test Case | TC-UT-001 | 測試案例 (Unit) |
| **TI** | Test Issue | TI-20260206-001 | 測試問題追蹤 |

### 編號格式規範

#### 報告類文件 (時間序列)
```
{TYPE}-{YYYYMMDD}-{SEQ}

範例:
  TP-20260206-001  ← 2026年2月6日的第1份測試計畫
  TR-20260206-002  ← 2026年2月6日的第2份測試報告
  RM-20260207-001  ← 2026年2月7日的第1份風險地圖
```

#### 測試案例 (功能分類)
```
TC-{LEVEL}-{MODULE}-{SEQ}

範例:
  TC-UT-PAYMENT-001  ← 單元測試 > Payment 模組 > 第1個案例
  TC-IT-API-015      ← 整合測試 > API > 第15個案例
  TC-E2E-CHECKOUT-003 ← E2E > Checkout 流程 > 第3個案例

Level 代碼:
  UT  = Unit Test
  IT  = Integration Test
  E2E = End-to-End Test
```

### 追溯關聯

```yaml
測試計畫 (TP-20260206-001)
  └── 引用 →
      ├── 風險地圖 (RM-20260206-001)
      ├── 測試案例:
      │   ├── TC-UT-PAYMENT-001
      │   ├── TC-UT-PAYMENT-002
      │   └── TC-IT-API-005
      └── 產出測試報告:
          └── TR-20260206-001

測試報告 (TR-20260206-001)
  └── 關聯 →
      ├── 測試計畫: TP-20260206-001
      ├── 執行結果:
      │   ├── TC-UT-PAYMENT-001: PASS ✅
      │   ├── TC-UT-PAYMENT-002: FAIL ❌
      │   └── TC-IT-API-005: PASS ✅
      └── 發現問題:
          └── TI-20260206-001 (PAYMENT-002 失敗原因)
```

---

## 檔案命名規範

### 測試檔案
```yaml
單元測試:
  格式: {module-name}.test.{ext}
  範例: payment-service.test.ts
  位置: tests/unit/{category}/

整合測試:
  格式: {feature-name}.integration.test.{ext}
  範例: user-api.integration.test.ts
  位置: tests/integration/{category}/

E2E 測試:
  格式: {scenario-name}.spec.{ext}
  範例: checkout-flow.spec.ts
  位置: tests/e2e/scenarios/
```

### Sentinel 產出報告
```yaml
測試計畫:
  格式: TP-{YYYYMMDD}-{SEQ}.md
  範例: TP-20260206-001.md
  位置: tests/reports/test-plans/
  包含: 測試範圍、風險分析、策略建議

測試報告:
  格式: TR-{YYYYMMDD}-{SEQ}.{md|html}
  範例: TR-20260206-001.md
  位置: tests/reports/test-reports/
  包含: 執行結果、覆蓋率、失敗分析

風險地圖:
  格式: RM-{YYYYMMDD}-{SEQ}.{md|json}
  範例: RM-20260206-001.md
  位置: tests/reports/risk-maps/
  包含: 高風險區域、複雜度分析、優先級排序

品質報告:
  格式: QR-{YYYYMMDD}-{SEQ}.{md|html}
  範例: QR-20260206-001.md
  位置: tests/reports/quality-reports/
  包含: 趨勢分析、技術債務、改進建議
```

---

## 報告內容規範

### 測試計畫 (TP) 必要欄位

```markdown
---
document_id: TP-20260206-001
title: "AuraTrade Trading Module 測試計畫"
created: 2026-02-06T10:30:00+08:00
author: Sentinel Agent v1.0.0
project: AuraTrade
version: 1.2.0
scope: src/features/trading/
risk_level: High
---

# 測試計畫: TP-20260206-001

## 1. 文件資訊
- **計畫編號:** TP-20260206-001
- **專案名稱:** AuraTrade
- **測試範圍:** Trading Module (v1.2.0)
- **風險等級:** High
- **建立日期:** 2026-02-06 10:30
- **負責人:** Development Team
- **預計執行:** 2026-02-07 ~ 2026-02-09

## 2. 追溯關聯
- **關聯需求:** REQ-TRADING-001, REQ-TRADING-005
- **關聯風險:** RM-20260206-001
- **產出報告:** TR-20260206-001 (待生成)

## 3. 測試案例清單
| 案例編號 | 類型 | 測試項目 | 優先級 | 狀態 |
|---------|------|---------|--------|------|
| TC-UT-TRADING-001 | Unit | calculateProfit() | P0 | Pending |
| TC-UT-TRADING-002 | Unit | validateOrder() | P0 | Pending |
| TC-IT-API-010 | Integration | POST /api/orders | P0 | Pending |
| TC-E2E-TRADING-001 | E2E | 完整下單流程 | P1 | Pending |

## 4. 風險識別
參照: RM-20260206-001
- Critical: tradingService.ts (Complexity: 15, Coverage: 45%)
- High: orderProcessor.ts (Complexity: 12, Coverage: 60%)

...
```

### 測試報告 (TR) 必要欄位

```markdown
---
document_id: TR-20260206-001
title: "AuraTrade Trading Module 測試報告"
created: 2026-02-06T15:45:00+08:00
author: Sentinel Agent v1.0.0
test_plan_id: TP-20260206-001
execution_time: 62.3s
overall_status: PASS_WITH_WARNINGS
---

# 測試報告: TR-20260206-001

## 1. 執行摘要
- **報告編號:** TR-20260206-001
- **關聯計畫:** TP-20260206-001
- **執行日期:** 2026-02-06 15:45
- **執行時長:** 62.3 秒
- **整體狀態:** PASS WITH WARNINGS ⚠️

## 2. 測試結果統計
| 測試類型 | 總數 | 通過 | 失敗 | 跳過 | 通過率 |
|---------|-----|------|------|------|--------|
| 單元測試 | 45 | 44 | 1 | 0 | 97.8% |
| 整合測試 | 12 | 12 | 0 | 0 | 100% |
| E2E 測試 | 3 | 3 | 0 | 0 | 100% |
| **總計** | **60** | **59** | **1** | **0** | **98.3%** |

## 3. 失敗案例分析
| 案例編號 | 測試項目 | 失敗原因 | 問題追蹤 | 影響範圍 |
|---------|---------|---------|---------|---------|
| TC-UT-TRADING-002 | validateOrder() | 未處理 null 值 | TI-20260206-001 | Medium |

## 4. 覆蓋率報告
- **整體覆蓋率:** 89.3%
- **單元測試:** 91.2%
- **整合測試:** 85.7%
- **高風險區域:** 76.5% (需提升至 90%+)

## 5. 追溯驗證
✅ 所有 P0 測試案例已執行
✅ 高風險區域 (RM-20260206-001) 已覆蓋
⚠️ TC-UT-TRADING-002 需修復 (見 TI-20260206-001)

...
```

### 風險地圖 (RM) 必要欄位

```markdown
---
document_id: RM-20260206-001
title: "AuraTrade 代碼風險地圖"
created: 2026-02-06T09:15:00+08:00
author: Sentinel Agent v1.0.0
scan_scope: src/
risk_threshold:
  critical: complexity > 15 AND coverage < 50%
  high: complexity > 10 AND coverage < 70%
  medium: complexity > 8 AND coverage < 80%
---

# 風險地圖: RM-20260206-001

## 1. 文件資訊
- **地圖編號:** RM-20260206-001
- **掃描範圍:** src/ (全專案)
- **掃描時間:** 2026-02-06 09:15
- **總檔案數:** 156
- **風險檔案數:** 8 (5.1%)

## 2. 風險分布

### 🔴 Critical 風險 (立即處理)
| 編號 | 檔案路徑 | 函數 | 複雜度 | 覆蓋率 | 優先級 |
|-----|---------|------|--------|--------|--------|
| RISK-001 | src/services/payment.ts | processPayment() | 15 | 45% | P0 |
| RISK-002 | src/services/trading.ts | executeTrade() | 16 | 42% | P0 |

### 🟡 High 風險 (優先處理)
| 編號 | 檔案路徑 | 函數 | 複雜度 | 覆蓋率 | 優先級 |
|-----|---------|------|--------|--------|--------|
| RISK-003 | src/auth/validateToken.ts | validateJWT() | 12 | 60% | P1 |
| RISK-004 | src/services/order.ts | processOrder() | 11 | 65% | P1 |

## 3. 視覺化熱圖

```
複雜度 vs 覆蓋率矩陣

20+ │           
    │           
15  │  ■ ■       [■ Critical]
    │  │ │       [□ High]
10  │  □ □       [· Medium]
    │  · ·       
5   │  · · · ·  
    │  · · · · · · ·
0   └─────────────────
    0%  25% 50% 75% 100%
         Coverage
```

## 4. 建議行動
- **RISK-001:** 拆分 processPayment() 為 3 個子函數
- **RISK-002:** 補充 8 個邊界測試案例
- **RISK-003:** 重構 validateJWT() 降低巢狀層級

...
```

---

## 追溯性矩陣範例

### 需求 → 測試案例 → 執行結果

```yaml
REQ-TRADING-001: 使用者應能建立市價訂單
  ├── TC-UT-TRADING-001: 驗證訂單資料格式
  │   └── TR-20260206-001: PASS ✅
  ├── TC-UT-TRADING-002: 驗證價格計算
  │   └── TR-20260206-001: FAIL ❌ (TI-20260206-001)
  ├── TC-IT-API-010: API 端點測試
  │   └── TR-20260206-001: PASS ✅
  └── TC-E2E-TRADING-001: 完整下單流程
      └── TR-20260206-001: PASS ✅

結論: 需求部分滿足 (75% 通過)
      需修復: TI-20260206-001
```

### 風險 → 測試策略 → 驗證結果

```yaml
RISK-001: payment.ts processPayment() (Complexity: 15, Coverage: 45%)
  ├── TP-20260206-001: 規劃 12 個測試案例
  │   ├── TC-UT-PAYMENT-001~008: 邊界條件測試
  │   └── TC-IT-API-005~008: 整合測試
  └── TR-20260206-001: 覆蓋率提升至 82% ✅
      └── 風險降級: Critical → Medium
```

---

## 檔案生命週期管理

### 報告封存策略
```yaml
條件: 報告超過 30 天
動作: 移動至 tests/reports/archives/{YYYY-MM}/

範例:
  TR-20260106-001.md → tests/reports/archives/2026-01/TR-20260106-001.md
  
保留策略:
  - 近 3 個月: 保留所有報告
  - 3-12 個月: 僅保留每週最後一份
  - 12 個月以上: 僅保留每月最後一份
```

### 測試案例版本控制
```yaml
變更追蹤:
  - 所有測試檔案納入 Git 版本控制
  - 報告檔案可選擇性 .gitignore
  
建議 .gitignore:
  tests/unit/coverage/
  tests/integration/coverage/
  tests/e2e/screenshots/
  tests/e2e/videos/
  tests/reports/archives/
```

---

## Sentinel 自動化規範

### 檔案產出時機

```yaml
掃描專案 [SC]:
  產出: 無 (僅顯示分析結果)

產生風險地圖 [RM]:
  產出: tests/reports/risk-maps/RM-{date}-{seq}.md
  格式: Markdown + JSON

生成測試 [GT]:
  產出: tests/{unit|integration|e2e}/{module}/{file}.test.ts
  備份: 若檔案存在,詢問覆蓋或合併

完整測試週期 [FC]:
  階段1: tests/reports/test-plans/TP-{date}-{seq}.md
  階段2-4: tests/{unit|integration|e2e}/ (測試檔案)
  階段5: tests/reports/test-reports/TR-{date}-{seq}.{md|html}

品質報告 [QR]:
  產出: tests/reports/quality-reports/QR-{date}-{seq}.{md|html}
```

### 編號自動遞增邏輯

```typescript
function generateDocumentId(type: string): string {
  const today = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const existingDocs = listFiles(`tests/reports/**/${type}-${today}-*.md`);
  const nextSeq = existingDocs.length + 1;
  return `${type}-${today}-${String(nextSeq).padStart(3, '0')}`;
}

// 範例使用
generateDocumentId('TP')  // → TP-20260206-001
generateDocumentId('TP')  // → TP-20260206-002 (同日第二份)
generateDocumentId('TR')  // → TR-20260206-001
```

---

## 檢查清單

### 建立新專案測試結構時
- [ ] 創建 tests/ 目錄結構 (unit/integration/e2e/reports/mocks)
- [ ] 複製 tests/README.md 範本
- [ ] 配置 .gitignore 排除暫存檔案
- [ ] 初始化測試框架配置 (jest.config.js / playwright.config.ts)

### 執行完整測試週期時
- [ ] 產生測試計畫 (TP-{date}-{seq}.md)
- [ ] 記錄所有測試案例編號 (TC-{level}-{module}-{seq})
- [ ] 產生測試報告 (TR-{date}-{seq}.md)
- [ ] 追溯驗證 (TP → TC → TR 完整關聯)

### 每月維護
- [ ] 封存舊報告至 archives/
- [ ] 檢查測試覆蓋率趨勢
- [ ] 更新風險地圖 (RM)
- [ ] 產生月度品質報告 (QR)

---

**版本:** 1.0.0  
**維護者:** Sentinel Agent  
**最後更新:** 2026-02-06
