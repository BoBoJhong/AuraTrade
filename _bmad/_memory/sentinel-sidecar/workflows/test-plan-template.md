# 測試計畫模板 (Test Plan Template)

**專案名稱:** [Project Name]  
**版本:** [Version]  
**日期:** [YYYY-MM-DD]  
**負責人:** [Developer Name]  
**Sentinel 版本:** 1.0.0

---

## 1. 測試目標 (Testing Objectives)

### 主要目標
- [ ] 驗證新功能正確性
- [ ] 確保現有功能無回歸
- [ ] 達成覆蓋率目標: ____%
- [ ] 識別高風險區域並補強
- [ ] 效能基準驗證

### 品質標準
```yaml
覆蓋率目標:
  核心邏輯: 90%+
  一般功能: 80%+
  工具函數: 70%+

通過率目標:
  單元測試: 98%+
  整合測試: 95%+
  E2E 測試: 100%

效能要求:
  單元測試總時長: < 5s
  整合測試總時長: < 20s
  E2E 平均場景: < 10s
```

---

## 2. 專案掃描結果 (Project Scan)

### 技術棧
```yaml
Frontend:
  Framework: [React/Vue/Angular]
  Testing: [Jest/Vitest/React Testing Library]
  Build: [Vite/Webpack/Turbopack]

Backend:
  Language: [Node.js/Python/Go]
  Framework: [Express/FastAPI/Gin]
  Testing: [Jest/Pytest/Go testing]

E2E:
  Tool: [Playwright/Cypress/Puppeteer]
  Browsers: [Chromium/Firefox/WebKit]
```

### 代碼統計
```yaml
總檔案數: ___
總程式碼行數: ___
平均 Cyclomatic Complexity: ___

高複雜度檔案 (> 10):
  - [file-path] (Complexity: ___)
  - [file-path] (Complexity: ___)

未測試檔案:
  - [file-path]
  - [file-path]
```

---

## 3. 測試範圍 (Testing Scope)

### 包含範圍
```yaml
新增功能:
  - [Feature 1] - src/features/feature1/
  - [Feature 2] - src/features/feature2/

修改區域:
  - [Component] - src/components/component.tsx
  - [Service] - src/services/service.ts

關鍵路徑:
  - 使用者登入流程
  - 資料處理流程
  - 支付流程
```

### 排除範圍
```yaml
不測試項目:
  - 第三方套件 (已測試)
  - 純型別定義檔案
  - 配置檔案
  - [其他排除項目]

原因說明:
  - [說明排除理由]
```

---

## 4. 風險分析 (Risk Assessment)

### 🔴 Critical 風險 (立即處理)

#### Risk #1: [檔案名稱]
```yaml
檔案: src/services/payment.ts
函數: processPayment()
風險等級: Critical
Complexity: 15
Coverage: 45%

風險因素:
  - 處理金額計算 (精度敏感)
  - 多重條件分支 (12 個 if/else)
  - 無邊界條件測試

影響範圍:
  - 使用者支付失敗 → 直接影響營收
  - 資料不一致 → 可能需要人工介入

建議行動:
  1. 新增 8 個邊界測試 (負數/零/極大值)
  2. 重構降低複雜度 (拆分子函數)
  3. 優先級: P0 (立即處理)
```

### 🟡 High 風險 (優先處理)

#### Risk #2: [檔案名稱]
```yaml
檔案: src/auth/validateToken.ts
函數: validateJWT()
風險等級: High
Complexity: 12
Coverage: 60%

風險因素:
  - 安全性相關 (認證邏輯)
  - 外部依賴 (jwt library)
  - 錯誤處理不完整

建議行動:
  1. 補充異常測試 (過期/偽造/格式錯誤 token)
  2. 加入 Mock 測試
  3. 優先級: P1 (本週完成)
```

### 🟢 Medium 風險 (建議優化)

```yaml
- src/utils/dateParser.ts (Complexity: 8, Coverage: 65%)
- src/helpers/formatters.ts (Complexity: 7, Coverage: 58%)
```

---

## 5. 測試策略 (Testing Strategy)

### 測試金字塔分配

```
        /\
       /  \  E2E (10%)
      /----\  8 scenarios
     /      \
    / 整合測試 \ (30%)
   /----------\  45 tests
  /            \
 /   單元測試    \ (60%)
/----------------\  152 tests
```

### 單元測試策略 (60% 工作量)
```yaml
重點:
  - 純函數邏輯測試
  - 邊界條件覆蓋
  - 錯誤處理驗證

框架: Jest/Vitest
工具: 
  - @testing-library/react (前端)
  - pytest-mock (後端)

優先測試:
  1. 高複雜度函數 (Complexity > 8)
  2. 金額/日期/字串處理
  3. 業務邏輯核心
```

### 整合測試策略 (30% 工作量)
```yaml
重點:
  - API 路由測試
  - 資料庫操作測試
  - 服務間協作測試

框架: Supertest (Node.js) / httpx (Python)
環境: Docker containers (PostgreSQL/Redis)

測試範圍:
  - 15 個 API endpoints
  - 8 個資料庫操作
  - 3 個服務整合
```

### E2E 測試策略 (10% 工作量)
```yaml
重點:
  - 關鍵使用者流程
  - 跨頁面互動
  - 真實瀏覽器行為

框架: Playwright
瀏覽器: Chromium (主要), Firefox (跨瀏覽器驗證)

場景清單:
  1. 使用者註冊 → 登入 → 編輯資料 → 登出
  2. 搜尋商品 → 加入購物車 → 結帳
  3. [其他關鍵場景]
```

---

## 6. 測試案例清單 (Test Cases)

### 單元測試

#### Module: Payment Service
| ID | 函數 | 測試案例 | 優先級 | 狀態 |
|----|------|---------|--------|------|
| UT-001 | processPayment() | 正常金額處理 | P0 | ⏳ Pending |
| UT-002 | processPayment() | 零金額拒絕 | P0 | ⏳ Pending |
| UT-003 | processPayment() | 負數金額拒絕 | P0 | ⏳ Pending |
| UT-004 | processPayment() | 超大金額處理 | P1 | ⏳ Pending |
| UT-005 | calculateFee() | 不同級距手續費 | P1 | ⏳ Pending |

#### Module: Authentication
| ID | 函數 | 測試案例 | 優先級 | 狀態 |
|----|------|---------|--------|------|
| UT-101 | validateJWT() | 有效 token 驗證 | P0 | ⏳ Pending |
| UT-102 | validateJWT() | 過期 token 拒絕 | P0 | ⏳ Pending |
| UT-103 | validateJWT() | 偽造 token 拒絕 | P0 | ⏳ Pending |

### 整合測試

#### API Tests
| ID | Endpoint | 測試案例 | 優先級 | 狀態 |
|----|----------|---------|--------|------|
| IT-001 | POST /api/login | 正確帳密登入 | P0 | ⏳ Pending |
| IT-002 | POST /api/login | 錯誤帳密拒絕 | P0 | ⏳ Pending |
| IT-003 | GET /api/users/:id | 取得使用者資料 | P1 | ⏳ Pending |
| IT-004 | PUT /api/users/:id | 更新使用者資料 | P1 | ⏳ Pending |

### E2E 測試

| ID | 場景 | 步驟 | 預期結果 | 優先級 | 狀態 |
|----|------|------|---------|--------|------|
| E2E-001 | 完整登入流程 | 1. 訪問首頁<br>2. 點擊登入<br>3. 輸入帳密<br>4. 送出 | 成功登入並跳轉 | P0 | ⏳ Pending |
| E2E-002 | 購物車流程 | 1. 搜尋商品<br>2. 加入購物車<br>3. 結帳 | 成功下單 | P0 | ⏳ Pending |

---

## 7. Mock 與測試數據 (Mocks & Test Data)

### Mock 需求
```yaml
External APIs:
  - Payment Gateway API
    - Mock 成功回應
    - Mock 失敗回應 (餘額不足/網路錯誤)
  
  - Email Service
    - Mock 發送成功
    - Mock 發送失敗

Database:
  - 使用 SQLite in-memory 或 Docker PostgreSQL
  - Seed data: users.sql, products.sql
```

### 測試數據
```yaml
Users:
  - valid_user: { id: 1, email: "test@example.com", role: "user" }
  - admin_user: { id: 999, email: "admin@example.com", role: "admin" }
  - invalid_user: { id: -1, email: "invalid", role: null }

Products:
  - normal_product: { id: 1, price: 1000, stock: 50 }
  - out_of_stock: { id: 2, price: 500, stock: 0 }
  - high_price: { id: 3, price: 999999, stock: 1 }
```

---

## 8. 執行排程 (Execution Schedule)

### 時程規劃
```yaml
Day 1-2: 單元測試開發與執行
  - 生成測試框架
  - 實作高風險區域測試
  - 覆蓋率目標: 80%+

Day 3: 整合測試開發與執行
  - API 測試實作
  - 資料庫測試實作
  - 覆蓋率目標: 75%+

Day 4: E2E 測試開發與執行
  - 關鍵場景錄製
  - 穩定性調整
  - 通過率目標: 100%

Day 5: 報告與修復
  - 生成測試報告
  - 修復失敗案例
  - 最終驗收
```

---

## 9. 成功標準 (Success Criteria)

### 必須達成 (Must Have)
- [ ] 單元測試覆蓋率 ≥ 85%
- [ ] 整合測試覆蓋率 ≥ 75%
- [ ] E2E 關鍵場景 100% 通過
- [ ] 所有 Critical 風險已修復
- [ ] 無 P0 失敗測試

### 期望達成 (Should Have)
- [ ] 整體覆蓋率 ≥ 90%
- [ ] 所有 High 風險已修復
- [ ] 測試執行時間 < 60s (含 E2E)

### 可選達成 (Nice to Have)
- [ ] 自動化 CI/CD 整合
- [ ] 效能回歸測試
- [ ] 視覺化測試報告

---

## 10. 備註 (Notes)

### 限制與假設
- 假設測試環境與正式環境配置一致
- 不包含效能測試 (另行規劃)
- 第三方 API 使用 Mock (避免真實扣款)

### 聯絡資訊
- 開發者: [Name / Email]
- Sentinel Agent: 自動產生報告至 `_bmad-output/test-reports/`

---

**模板版本:** 1.0.0  
**最後更新:** 2026-02-06  
**由 Sentinel Agent 自動生成**
