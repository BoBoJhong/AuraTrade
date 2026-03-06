# 完整測試週期工作流 (Full Test Cycle)

**目標：** 執行「測試計畫 → 單元測試 → 整合測試 → E2E 測試 → 測試報告」的完整流程

---

## 工作流觸發

**命令：** `*full-cycle` 或透過主選單 `[FC]`

**使用時機：**
- 新功能開發完成，需要完整測試驗證
- Pre-release 品質檢查
- CI/CD Pipeline 整合
- 重構後的回歸測試

---

## 階段 1: 測試計畫 (Test Plan)

### 輸入
- 專案目錄結構
- 新增或修改的代碼範圍
- 業務需求文件 (PRD/SRS)

### 處理流程
```yaml
1. 專案掃描:
   - 檢測技術棧 (React/Vue/Node.js/Python/FastAPI)
   - 識別測試框架 (Jest/Vitest/Pytest/Playwright)
   - 分析代碼複雜度 (Cyclomatic Complexity)

2. 風險評估:
   - 識別高風險區域 (Complexity > 10, Coverage < 50%)
   - 標記關鍵業務邏輯 (auth, payment, data processing)
   - 分析依賴關係與外部 API

3. 策略規劃:
   - 建議測試金字塔比例 (60% 單元, 30% 整合, 10% E2E)
   - 優先級排序 (Critical → High → Medium → Low)
   - 覆蓋率目標設定 (核心邏輯 90%+, 一般功能 80%+)
```

### 輸出
生成測試計畫檔案:
```yaml
檔案路徑: tests/reports/test-plans/TP-{YYYYMMDD}-{SEQ}.md
檔案格式: Markdown with YAML front matter
編號範例: TP-20260206-001

包含內容:
  - 文件追溯資訊 (document_id, version, scope)
  - 測試範圍清單 (包含/排除檔案)
  - 風險地圖引用 (RM-{date}-{seq})
  - 測試策略建議 (金字塔比例)
  - 測試案例清單 (TC-{level}-{module}-{seq})
  - 預估工作量與時程
```

---

## 階段 2: 單元測試 (Unit Tests)

### 輸入
- Test Plan 中標記的檔案清單
- 代碼邏輯與函數簽名

### 處理流程
```yaml
1. 自動生成測試:
   - 解析函數簽名與邏輯流程
   - 生成正常案例測試 (Happy Path)
   - 生成邊界條件測試 (null/undefined/空值/極端值)
   - 生成錯誤處理測試 (異常拋出與捕獲)

2. Mock 準備:
   - 自動生成 Mock 物件 (API/Database/外部依賴)
   - 配置測試環境變數
   - 產出樣板代碼

3. 執行測試:
   - 運行測試套件
   - 收集覆蓋率數據
   - 記錄失敗案例
```

### 輸出
```yaml
測試檔案:
  路徑: tests/unit/{module}/{filename}.test.{ts|py}
  範例: tests/unit/services/payment.test.ts
  編號: 檔案內包含 TC-UT-{MODULE}-{SEQ} 測試案例

覆蓋率報告:
  路徑: tests/unit/coverage/lcov-report/index.html
  格式: HTML + lcov.info
  指標: 行覆蓋率、分支覆蓋率、函數覆蓋率

執行紀錄:
  失敗案例: 記錄至測試報告 (TR-{date}-{seq})
  案例狀態: PASS/FAIL/SKIP
  執行時間: 毫秒級精度
```

---

## 階段 3: 整合測試 (Integration Tests)

### 輸入
- API 路由定義
- 資料庫 Schema
- 服務間依賴關係

### 處理流程
```yaml
1. API 測試生成:
   - 掃描 API endpoints (Express/FastAPI routes)
   - 生成請求/回應測試 (Supertest/httpx)
   - 測試狀態碼、Schema 驗證、錯誤處理

2. 資料庫整合:
   - 配置測試資料庫 (SQLite in-memory/Docker containers)
   - 生成測試數據 (符合 Schema 約束)
   - 測試 CRUD 操作與交易完整性

3. 服務整合:
   - 測試多模組協作 (例: Auth + User Service)
   - 驗證資料流轉正確性
```

### 輸出
```yaml
測試檔案:
  API 測試: tests/integration/api/{route-name}.integration.test.ts
  資料庫測試: tests/integration/database/{entity-name}.integration.test.ts
  服務測試: tests/integration/services/{service-name}.integration.test.ts
  編號: 檔案內包含 TC-IT-{MODULE}-{SEQ} 測試案例

覆蓋率報告:
  路徑: tests/integration/coverage/lcov-report/index.html
  重點: API endpoint 覆蓋率、資料庫操作覆蓋率

失敗分析:
  記錄至: 測試報告 (TR-{date}-{seq})
  包含: 失敗案例編號、原因分析、修復建議
```

---

## 階段 4: E2E 測試 (End-to-End Tests)

### 輸入
- 使用者流程 (User Stories)
- UI 頁面結構
- 關鍵業務場景

### 處理流程
```yaml
1. 場景識別:
   - 分析使用者流程 (登入 → 瀏覽 → 交易 → 登出)
   - 標記關鍵路徑 (Critical User Journeys)
   - 識別跨平台需求 (Desktop/Mobile/Browser)

2. Playwright 測試生成:
   - 自動錄製使用者操作
   - 生成穩定的選擇器 (data-testid > text > CSS)
   - 加入 waiting 策略 (網路請求完成, 元素可見)

3. 執行與監控:
   - 運行 E2E 測試套件
   - 截圖/錄影失敗案例
   - 收集效能數據 (頁面載入時間)
```

### 輸出
```yaml
測試檔案:
  場景測試: tests/e2e/scenarios/{scenario-name}.spec.ts
  範例: tests/e2e/scenarios/checkout-flow.spec.ts
  編號: 檔案內包含 TC-E2E-{SCENARIO}-{SEQ} 測試案例

測試數據:
  Fixtures: tests/e2e/fixtures/{data-name}.json
  範例: tests/e2e/fixtures/test-users.json

執行產物:
  截圖: tests/e2e/screenshots/{test-name}-{timestamp}.png (失敗時)
  錄影: tests/e2e/videos/{test-name}-{timestamp}.webm (失敗時)
  HTML報告: playwright-report/index.html

效能指標:
  記錄至: 測試報告 (TR-{date}-{seq})
  指標: 頁面載入時間、First Contentful Paint、Time to Interactive
```

---

## 階段 5: 測試報告 (Test Report)

### 彙總數據
```yaml
單元測試:
  - 總測試數: 152
  - 通過率: 98.7% (150/152)
  - 覆蓋率: 87.3%
  - 執行時間: 3.2s

整合測試:
  - 總測試數: 45
  - 通過率: 95.6% (43/45)
  - 覆蓋率: 82.1%
  - 執行時間: 12.5s

E2E 測試:
  - 總場景數: 8
  - 通過率: 100%
  - 平均頁面載入: 1.2s
  - 執行時間: 45.3s
```

### 風險分析
```yaml
高風險區域 (需立即處理):
  - src/services/payment.ts (Complexity: 15, Coverage: 45%)
  - src/auth/validateToken.ts (Complexity: 12, Coverage: 60%)

中風險區域 (建議優化):
  - src/utils/dateParser.ts (Complexity: 8, Coverage: 65%)

已修復風險:
  - src/api/userRoutes.ts (原 Complexity: 14 → 8)
```

### 輸出格式
```yaml
主報告:
  路徑: tests/reports/test-reports/TR-{YYYYMMDD}-{SEQ}.md
  編號: TR-20260206-001
  格式: Markdown with YAML front matter
  
HTML版本:
  路徑: tests/reports/test-reports/TR-{YYYYMMDD}-{SEQ}.html
  包含: 互動式圖表、可展開的失敗詳情、下載連結

追溯關聯:
  關聯計畫: TP-{date}-{seq} (測試計畫編號)
  關聯風險: RM-{date}-{seq} (風險地圖編號)
  執行案例: TC-{level}-{module}-{seq} (所有測試案例)
  
報告內容:
  1. 執行摘要
     - 整體通過率、覆蓋率、執行時間
     - 各層級 (單元/整合/E2E) 統計
  
  2. 測試案例執行結果
     | 案例編號 | 狀態 | 執行時間 | 錯誤訊息 |
     |---------|------|---------|----------|
     | TC-UT-PAYMENT-001 | PASS ✅ | 12ms | - |
     | TC-UT-PAYMENT-002 | FAIL ❌ | 8ms | Null value error |
  
  3. 風險地圖更新
     - 原風險: RM-{date}-{seq}
     - 覆蓋率變化: 45% → 82%
     - 風險降級: Critical → Medium
  
  4. 失敗案例分析
     - 案例編號、失敗原因、Stack Trace
     - 建議修復方案、預估工作量
  
  5. 趨勢分析 (與上次比較)
     - 覆蓋率趨勢圖
     - 通過率趨勢圖
     - 執行時間趨勢圖
  
  6. 改進建議
     - 優先處理項目 (P0/P1 失敗案例)
     - 技術債務清單
     - 下次測試重點
```

---

## 流程控制

### 中斷條件
```yaml
critical_failure:
  - 單元測試通過率 < 95%
  - 高風險區域覆蓋率 < 70%
  - E2E 關鍵場景失敗

action:
  - 停止流程
  - 產出當前階段報告
  - 提供修復建議
```

### 跳過條件
```yaml
skip_integration:
  - 純前端專案 (無 API)
  - 單元測試失敗率 > 10%

skip_e2e:
  - CLI 工具專案
  - 整合測試失敗率 > 5%
```

---

## 使用範例

### 基本使用
```
開發者: *full-cycle
Sentinel: 
  🛡️ 開始完整測試週期...
  
  [1/5] 測試計畫生成中...
  ✅ 識別到 23 個檔案需要測試
  ⚠️  發現 3 個高風險區域
  📋 測試計畫已生成: tests/reports/test-plans/TP-20260206-001.md
  📋 風險地圖已生成: tests/reports/risk-maps/RM-20260206-001.md
  
  [2/5] 單元測試執行中...
  ✅ 生成 152 個測試案例 (TC-UT-*-001 ~ TC-UT-*-152)
  ✅ 通過率 98.7% (150/152)
  📊 覆蓋率 87.3%
  ❌ 失敗案例:
     - TC-UT-PAYMENT-023: Null pointer exception
     - TC-UT-AUTH-045: Token validation timeout
  
  [3/5] 整合測試執行中...
  ✅ 測試 15 個 API endpoints (TC-IT-API-001 ~ TC-IT-API-015)
  ⚠️  2 個測試失敗:
     - TC-IT-API-008: Database connection timeout
     - TC-IT-API-012: Invalid response schema
  
  [4/5] E2E 測試執行中...
  ✅ 8 個場景全部通過 (TC-E2E-*-001 ~ TC-E2E-*-008)
  ⏱️  平均載入時間 1.2s
  📸 截圖已儲存至 tests/e2e/screenshots/
  
  [5/5] 測試報告生成中...
  📄 測試報告: tests/reports/test-reports/TR-20260206-001.md
  📄 HTML版本: tests/reports/test-reports/TR-20260206-001.html
  
  🎉 測試週期完成！
  
  📊 執行摘要:
     - 文件編號: TR-20260206-001
     - 關聯計畫: TP-20260206-001
     - 關聯風險: RM-20260206-001
     - 整體通過率: 97.5% (195/200)
     - 執行時長: 62.3s
  
  ⚠️  需處理失敗案例:
     1. TC-UT-PAYMENT-023 (詳見報告第 3.2 節)
     2. TC-UT-AUTH-045 (詳見報告第 3.3 節)
     3. TC-IT-API-008 (詳見報告第 3.4 節)
     4. TC-IT-API-012 (詳見報告第 3.5 節)
  
  💡 建議行動:
     - 優先修復 payment.ts 的 Null 檢查 (P0)
     - 增加 API timeout 設定 (P1)
     - 參考 TR-20260206-001 第 6 節改進建議
```

### 進階選項
```
開發者: *full-cycle --scope=src/features/trading --skip-e2e
Sentinel:
  🛡️ 執行範圍測試 (trading 模組)
  ⏭️  已跳過 E2E 測試
  
  [1/4] 測試計畫: 發現 8 個檔案...
  ...
```

---

## 整合 CI/CD

### GitHub Actions 範例
```yaml
name: Full Test Cycle

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: npm install
      - name: Run full test cycle
        run: npm run test:full
      - name: Upload test report
        uses: actions/upload-artifact@v3
        with:
          name: test-report
          path: test-report-*.html
```

---

## 效能優化

### 平行執行
```yaml
並行策略:
  - 單元測試: 按檔案分組平行執行
  - 整合測試: 按 API 模組平行執行
  - E2E 測試: 按場景平行執行 (獨立瀏覽器)

預期加速:
  - 單元測試: 3.2s → 1.1s (3x)
  - 整合測試: 12.5s → 4.8s (2.6x)
  - E2E 測試: 45.3s → 18.2s (2.5x)
```

---

**版本:** 1.0.0  
**創建日期:** 2026-02-06  
**維護者:** Sentinel Agent
