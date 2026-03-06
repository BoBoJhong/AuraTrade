# 增量測試工作流 (Incremental Testing)

**目標：** 只測試變更的檔案，大幅縮短測試時間（省時 60-90%）

---

## 觸發時機

**命令：** `*quick-test` 或 `*incremental`

**適用情境：**
- 開發過程中頻繁測試
- Git commit 前快速驗證
- PR 提交前初步檢查

**不適用情境：**
- 重構涉及多個模組
- Release 前完整驗證 (應使用 *full-cycle)
- 首次執行測試 (無歷史記錄)

---

## 階段 1: 變更檢測 (Change Detection)

### 1.1 Git Diff 分析

```yaml
檢測策略:
  1. 執行 git diff:
     git diff --name-only HEAD
     → 取得所有變更檔案清單
  
  2. 過濾測試相關檔案:
     src/services/payment.ts        → 需要測試
     src/components/Button.tsx      → 需要測試
     README.md                      → 跳過
     docs/API.md                    → 跳過
  
  3. 識別測試檔案:
     tests/unit/payment.test.ts     → 直接執行
     src/services/payment.ts        → 找對應測試檔

輸出範例:
  變更檔案: 5 個
  需要測試: 3 個
  跳過測試: 2 個 (文件類)
```

### 1.2 依賴圖分析

```yaml
依賴追蹤:
  若 utils/format.ts 變更:
    → 檢查哪些檔案 import format.ts
    → services/payment.ts (使用 format)
    → components/PriceDisplay.tsx (使用 format)
    → 標記這些檔案為「間接變更」
  
  測試範圍:
    直接變更: utils/format.ts
    間接影響: payment.ts, PriceDisplay.tsx
    → 執行所有相關測試

工具支援:
  - madge (JavaScript dependency graph)
  - pydeps (Python dependency graph)
  - 手動解析 import 語句
```

### 1.3 快取檢查

```yaml
檢查 change-tracker.yaml:
  file_checksums:
    "src/services/payment.ts":
      last_hash: "abc123def456"
      last_test: "2026-02-06T14:30:00"
      last_result: "PASSED"
  
  若檔案 hash 未變更:
    → 跳過測試（使用快取結果）
  
  若檔案已變更:
    → 更新 hash 並執行測試
```

---

## 階段 2: 智慧測試選擇 (Smart Test Selection)

### 2.1 測試優先級

```yaml
優先級排序:
  Level 1 - Critical (必測):
    - 標記為 @critical 的測試
    - 涉及 payment/auth/security 的變更
    - 上次失敗的測試
  
  Level 2 - High (高優先):
    - 直接變更的檔案測試
    - 複雜度 > 10 的函數
    - 覆蓋率 < 80% 的區域
  
  Level 3 - Medium (可選):
    - 間接影響的測試
    - 低風險工具函數
    - 覆蓋率 > 90% 的穩定區域

快速模式:
  只執行 Level 1 + Level 2
  Level 3 留待 *full-cycle
```

### 2.2 測試類型選擇

```yaml
根據變更範圍選擇:
  
  僅工具函數變更:
    → 單元測試即可
    → 跳過整合測試與 E2E
  
  API 端點變更:
    → 單元測試 + 整合測試
    → 跳過 E2E (除非關鍵流程)
  
  UI 元件變更:
    → 單元測試 + E2E (視覺回歸)
    → 跳過後端整合測試
  
  資料庫 Schema 變更:
    → 單元測試 + 整合測試 + E2E
    → 全面測試 (高風險)
```

---

## 階段 3: 增量測試執行 (Incremental Execution)

### 3.1 並行執行策略

```yaml
最大化效率:
  1. 識別獨立測試:
     tests/unit/payment.test.ts
     tests/unit/format.test.ts
     → 可並行執行 (無依賴)
  
  2. 隔離依賴測試:
     tests/integration/api/orders.test.ts
     → 需要資料庫 (序列執行)
  
  3. 工作分配:
     並行池: 4 個 worker (根據 CPU 核心數)
     tests/unit/* → Worker 1-4 並行
     tests/integration/* → Worker 1 序列
     tests/e2e/* → 按需執行

預期加速:
  原本: 120 秒 (全部測試)
  增量: 18 秒 (只測試變更)
  加速比: 6.7x
```

### 3.2 快取復用

```yaml
使用上次結果:
  tests/unit/utils.test.ts:
    last_result: "PASSED (10/10)"
    file_hash: "xyz789" (未變更)
    → 標記為 ✅ CACHED
  
  終端顯示:
    ✅ payment.test.ts - 5/5 passed (NEW)
    ✅ format.test.ts - 3/3 passed (NEW)
    ✅ utils.test.ts - 10/10 cached (SKIP)
    
    Total: 18/18 passed (12 seconds, 6x faster)
```

---

## 階段 4: 結果報告 (Incremental Report)

### 4.1 簡化報告格式

```markdown
# 增量測試報告 (TR-INC-20260206-001)

**執行時間:** 2026-02-06 15:30:00  
**測試模式:** Incremental (Quick Test)  
**Git Commit:** abc123d  

---

## 📊 執行摘要

| 項目 | 數值 |
|------|------|
| 變更檔案 | 5 個 |
| 執行測試 | 23 個 (↓87 個快取) |
| 執行時間 | 12 秒 (↓108 秒 vs 完整測試) |
| 通過率 | 100% (23/23) |
| 加速比 | **10x** |

---

## 🔍 測試範圍

### 直接變更
- `src/services/payment.ts` → 5 tests ✅
- `src/utils/format.ts` → 3 tests ✅

### 間接影響
- `src/components/PriceDisplay.tsx` → 8 tests ✅

### 快取復用
- `tests/unit/auth.test.ts` → 15 tests ✅ (cached)
- `tests/integration/api.test.ts` → 42 tests ✅ (cached)

---

## ⚠️  風險提示

**未執行的測試區域:**
- E2E 測試 (87 個) - 建議 Release 前執行 *full-cycle
- 整合測試 (42 個) - 已快取，若涉及 API 變更請重跑

**建議行動:**
- ✅ 可安全 commit (所有變更測試通過)
- ⚠️  PR merge 前建議執行 *full-cycle

---

**測試計畫:** TP-20260206-001  
**上次完整測試:** 2026-02-05 (TR-20260205-003)
```

### 4.2 差異比較

```yaml
與上次測試比較:
  新增測試:
    + tests/unit/payment.test.ts::should_handle_refund
  
  修復測試:
    ✅ tests/unit/format.test.ts::should_format_currency
       (上次失敗 → 本次通過)
  
  降級測試:
    ❌ tests/unit/discount.test.ts::should_calculate_discount
       (上次通過 → 本次失敗)

自動產生 Issue:
  若有新失敗測試 → 立即產生修復建議
```

---

## 階段 5: 更新追蹤檔 (Update Tracker)

### 5.1 更新 change-tracker.yaml

```yaml
# change-tracker.yaml (自動更新)
last_scan:
  timestamp: "2026-02-06T15:30:00+08:00"
  commit_hash: "abc123d"
  test_mode: "incremental"

file_checksums:
  "src/services/payment.ts":
    last_hash: "new_hash_456"
    last_test: "2026-02-06T15:30:00"
    last_result: "PASSED"
    test_count: 5
  
  "src/utils/format.ts":
    last_hash: "updated_789"
    last_test: "2026-02-06T15:30:00"
    last_result: "PASSED"
    test_count: 3

dependency_graph:
  "src/utils/format.ts":
    used_by:
      - "src/services/payment.ts"
      - "src/components/PriceDisplay.tsx"

change_history:
  - timestamp: "2026-02-06T15:30:00"
    files_changed: 5
    tests_run: 23
    tests_cached: 87
    duration: 12
    result: "PASSED"
```

---

## 使用範例

### 範例 1: 開發中快速驗證

```bash
# 開發者修改 payment.ts
開發者: (編輯 src/services/payment.ts)

# 快速測試
開發者: *quick-test

Sentinel:
  🔍 檢測變更...
  
  變更檔案: 1 個
  - src/services/payment.ts (modified)
  
  🧪 執行測試...
  ✅ tests/unit/services/payment.test.ts - 5/5 passed (3.2s)
  ✅ tests/integration/api/payment.test.ts - 8/8 passed (4.1s)
  
  📊 摘要:
  - 執行測試: 13 個
  - 快取測試: 97 個
  - 總耗時: 7.3 秒 (vs 120 秒完整測試)
  - 加速比: 16x
  
  ✅ 所有測試通過！可安全 commit
```

### 範例 2: 多檔案變更

```bash
開發者: (修改 3 個檔案)
         - src/services/payment.ts
         - src/utils/format.ts
         - src/components/PriceDisplay.tsx

開發者: *quick-test

Sentinel:
  🔍 檢測變更...
  
  直接變更: 3 個檔案
  間接影響: 2 個檔案 (依賴分析)
  
  📊 測試範圍:
  - 單元測試: 16 個 (需執行)
  - 整合測試: 8 個 (需執行)
  - E2E 測試: 0 個 (跳過，低風險變更)
  - 快取測試: 86 個 (復用上次結果)
  
  🧪 執行測試...
  ✅ 單元測試 - 16/16 passed (8.2s)
  ✅ 整合測試 - 8/8 passed (5.4s)
  
  📊 摘要:
  - 執行測試: 24 個
  - 快取測試: 86 個
  - 總耗時: 13.6 秒
  - 加速比: 8.8x
  
  ✅ 所有測試通過！
```

### 範例 3: 關鍵變更觸發完整測試

```bash
開發者: (修改 backend/models/payment.py - 資料庫 Schema)

開發者: *quick-test

Sentinel:
  🔍 檢測變更...
  
  ⚠️  檢測到關鍵變更:
  - 資料庫 Schema 變更 (payment model)
  
  📊 風險評估:
  - 變更類型: HIGH RISK
  - 影響範圍: 資料庫層
  - 建議: 完整測試
  
  ❓ 檢測到高風險變更
  
  選項:
  [A] 執行完整測試週期 (推薦)
  [B] 僅執行增量測試 (風險自負)
  
  選擇: [A]

Sentinel:
  切換至完整測試模式...
  → 執行 *full-cycle
  
  [執行完整測試流程...]
```

---

## 效能優化

### 快取策略

```yaml
快取層級:
  Level 1 - 檔案層級:
    檔案未變更 → 跳過所有相關測試
  
  Level 2 - 函數層級:
    只測試變更的函數 (需 AST 解析)
  
  Level 3 - 測試結果層級:
    上次通過 + 代碼未變 → 直接復用結果

快取失效條件:
  - 測試檔案本身變更
  - 依賴的 Mock 資料變更
  - 環境變數變更 (.env)
  - 測試框架版本變更
```

### 並行優化

```yaml
Worker Pool:
  CPU 核心數: 8
  Worker 數量: 6 (預留 2 核心給系統)
  
  分配策略:
    單元測試: 4 workers 並行
    整合測試: 1 worker (資料庫鎖)
    E2E 測試: 1 worker (瀏覽器資源)

記憶體管理:
  單測試最大記憶體: 512MB
  超過限制 → 序列執行
```

---

## 錯誤處理

### 常見問題

#### 問題 1: 依賴圖不完整
```yaml
症狀:
  修改 A.ts 但未執行依賴 A 的 B.ts 測試
  
解決:
  1. 強制重建依賴圖: *reinit
  2. 手動標記依賴: .sentinel-config.yaml
     custom:
       manual_dependencies:
         "src/utils/format.ts":
           - "src/services/payment.ts"
```

#### 問題 2: 快取污染
```yaml
症狀:
  檔案已變更但仍使用舊結果
  
解決:
  1. 清除快取: *clear-cache
  2. 執行完整測試: *full-cycle --no-cache
  3. 檢查 change-tracker.yaml 的 hash 值
```

#### 問題 3: Git 未追蹤的檔案
```yaml
症狀:
  新檔案未被檢測到變更
  
解決:
  1. git add 新檔案
  2. 或手動指定: *quick-test --file=new-file.ts
```

---

## 組合使用

### 開發工作流

```bash
# 1. 開發階段 - 頻繁快速測試
*quick-test  # 每次儲存後執行 (10-20 秒)

# 2. Commit 前 - 驗證變更
*quick-test  # 確保沒有破壞既有功能

# 3. PR 前 - 完整驗證
*full-cycle  # 執行所有測試 (2-5 分鐘)

# 4. Release 前 - 品質報告
*quality-report  # 產生完整品質評估
```

### CI/CD 整合

```yaml
# .github/workflows/pr-check.yml
on: pull_request
jobs:
  incremental-test:
    runs-on: ubuntu-latest
    steps:
      - name: Quick Test (變更檔案)
        run: sentinel *quick-test
        timeout: 5min
  
  full-test:
    runs-on: ubuntu-latest
    if: contains(github.event.pull_request.labels.*.name, 'needs-full-test')
    steps:
      - name: Full Cycle
        run: sentinel *full-cycle
        timeout: 15min
```

---

## 效能指標

### 預期加速比

| 變更範圍 | 完整測試 | 增量測試 | 加速比 |
|---------|---------|---------|--------|
| 單一檔案 | 120s | 8s | **15x** |
| 3-5 檔案 | 120s | 15s | **8x** |
| 整個模組 | 120s | 45s | **2.7x** |
| 關鍵變更 | 120s | 120s | 1x (回退完整測試) |

### 真實案例

**AuraTrade 專案:**
- 檔案總數: 156
- 測試總數: 342
- 完整測試: 118 秒
- 增量測試 (平均): 14 秒
- **實際加速: 8.4x**

---

**版本:** 1.0.0  
**維護者:** Sentinel Agent  
**最後更新:** 2026-02-06  
**推薦使用:** 開發階段 + Commit 前驗證
