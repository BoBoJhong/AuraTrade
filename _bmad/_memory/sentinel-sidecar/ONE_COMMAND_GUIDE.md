# Sentinel Agent 一鍵測試指南

**適用情境：** 程式碼開發完成，需要執行完整測試驗證

---

## 🎯 核心命令對比

### 開發階段 vs 完成驗證

```bash
# ❌ 錯誤理解 - 需要自己一步步執行
開發者: 先掃描，再生成測試，再執行，再看報告...
Sentinel: (需要多個命令)

# ✅ 正確使用 - 一鍵完成所有工作
開發者: *full-cycle
Sentinel: [自動執行完整流程，最終產出測試報告]
```

---

## 🚀 完整測試一鍵執行

### 情境 1: 功能開發完成，第一次執行測試

```bash
# 步驟 1: 初始化專案 (首次使用)
*init

Sentinel:
  🔍 自動檢測專案...
  ✅ 配置檔案: .sentinel-config.yaml
  ✅ 測試目錄: tests/
  
# 步驟 2: 一鍵完整測試
*full-cycle

Sentinel:
  🛡️ Sentinel 完整測試週期啟動
  
  [階段 1/5] 生成測試計畫...
  ✅ tests/reports/test-plans/TP-20260206-001.md
  
  [階段 2/5] 執行單元測試...
  🧪 自動生成 23 個測試案例
  ✅ tests/unit/ (23/23 passed - 92% coverage)
  
  [階段 3/5] 執行整合測試...
  🧪 自動生成 8 個 API 測試
  ✅ tests/integration/ (8/8 passed)
  
  [階段 4/5] 執行 E2E 測試...
  🧪 識別 3 個關鍵流程
  ✅ tests/e2e/ (3/3 passed)
  
  [階段 5/5] 產出測試報告...
  ✅ tests/reports/test-reports/TR-20260206-001.md
  
  🎉 測試週期完成！
  
  📊 整體結果:
  - 總測試: 34 個
  - 通過率: 100%
  - 覆蓋率: 89%
  - 耗時: 2 分 18 秒
  
  📋 測試報告:
  → tests/reports/test-reports/TR-20260206-001.md
  
  ✅ 品質符合標準，可以 commit！
```

**就這麼簡單！一個命令完成所有測試！**

---

### 情境 2: 程式碼修改後快速驗證 (推薦)

```bash
# 開發階段 - 頻繁測試 (快)
開發者: (修改 payment.ts)
開發者: *quick-test

Sentinel:
  🔍 檢測變更... 1 個檔案
  🧪 執行測試... 5 個 (跳過 87 個快取)
  ✅ 所有測試通過！(12 秒)
  
# PR 前 - 完整驗證 (慢但完整)
開發者: *full-cycle

Sentinel:
  [執行完整測試流程...]
  ✅ 所有測試通過！(2 分 18 秒)
  📋 完整報告已產出
```

---

### 情境 3: 測試失敗時的互動處理

```bash
開發者: *full-cycle

Sentinel:
  [階段 2/5] 執行單元測試...
  
  ❌ tests/unit/payment.test.ts 
     - should_process_payment ✅ PASSED
     - should_reject_negative_amount ❌ FAILED
       Expected: throw Error
       Actual: returned { success: false }
  
  🔍 失敗分析:
  - 原因: payment.ts 缺少參數驗證
  - 影響: 1 個測試 (4.3% of unit tests)
  
  💡 修復建議:
  ```typescript
  // src/services/payment.ts (Line 15)
  function processPayment(amount: number) {
    if (amount < 0) {
      throw new Error('Amount cannot be negative');  // 加入這行
    }
    // ...
  }
  ```
  
  ❓ 下一步行動:
  [A] 查看詳細錯誤訊息
  [B] 自動套用修復建議
  [C] 標記為 Known Issue 並繼續
  [D] 中斷測試週期
  
  選擇: [A/B/C/D]

開發者: B

Sentinel:
  ✅ 修復已套用至 src/services/payment.ts
  🔄 重新執行測試...
  ✅ tests/unit/payment.test.ts (5/5 passed)
  
  繼續執行階段 3...
```

---

## 📊 兩種測試模式對比

### *quick-test (增量測試)

**使用時機:**
- 開發過程中頻繁測試
- Commit 前快速驗證
- 確認改動沒有破壞現有功能

**特色:**
- ⚡ 超快速 (10-20 秒)
- 🎯 只測試變更檔案
- 💾 使用快取結果
- ⚠️ 不產出完整報告

```bash
*quick-test

輸出:
  變更: 3 檔案
  測試: 15 個 (快取 87 個)
  耗時: 12 秒 (10x faster)
  結果: ✅ 通過
```

### *full-cycle (完整測試)

**使用時機:**
- 功能開發完成
- PR 提交前
- Release 前驗證
- 需要完整測試報告

**特色:**
- 🔍 測試所有代碼
- 📋 產出完整報告 (含風險地圖)
- 🎯 涵蓋單元/整合/E2E
- ⏱️ 耗時較長 (2-5 分鐘)

```bash
*full-cycle

輸出:
  階段 1-5: 全部完成
  測試: 102 個
  耗時: 2 分 18 秒
  結果: ✅ 通過
  報告: TR-20260206-001.md
```

---

## 💡 實戰推薦工作流

### 完美的測試流程

```bash
# 1. 專案啟動 (首次)
*init  # 只需一次，自動檢測並配置

# 2. 開發階段 (每次修改後)
*quick-test  # 快速驗證 (10-20 秒)

# 3. 功能完成 (準備 commit)
*quick-test  # 最後一次快速檢查

# 4. PR 提交前 (重要！)
*full-cycle  # 完整測試 (2-5 分鐘)

# 5. 查看測試報告
open tests/reports/test-reports/TR-20260206-001.md
```

### 時間對比

| 階段 | 命令 | 耗時 | 次數/天 | 總耗時 |
|------|------|------|---------|--------|
| 開發中 | *quick-test | 12s | 20 次 | 4 分鐘 |
| Commit前 | *quick-test | 12s | 5 次 | 1 分鐘 |
| PR前 | *full-cycle | 138s | 1 次 | 2.3 分鐘 |
| **總計** | | | **26 次** | **7.3 分鐘** |

**vs 傳統手動測試:** 每次 5 分鐘 × 26 次 = 130 分鐘  
**省時:** **122.7 分鐘/天** (94% 時間節省)

---

## 🎓 進階使用

### 1. 自訂測試範圍

```bash
# 只測試特定模組
*full-cycle --module=src/services/

# 跳過 E2E 測試
*full-cycle --skip-e2e

# 強制執行 (即使單元測試失敗)
*full-cycle --force
```

### 2. 測試失敗自動修復

```yaml
# .sentinel-config.yaml
test_strategy:
  auto_fix: true  # 啟用自動修復建議
  
  fix_confidence_threshold: 0.8  # 信心度 > 80% 自動套用
```

啟用後：
```bash
*full-cycle

Sentinel:
  ❌ 測試失敗
  💡 修復建議 (信心度: 92%)
  ✅ 自動套用修復
  🔄 重新測試
  ✅ 測試通過
```

### 3. CI/CD 整合

```yaml
# .github/workflows/test.yml
name: Sentinel Full Test

on: 
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node.js
        uses: actions/setup-node@v2
      
      - name: Install Dependencies
        run: npm install
      
      - name: Run Sentinel Full Cycle
        run: |
          # Sentinel 自動載入 .sentinel-config.yaml
          sentinel *full-cycle
      
      - name: Upload Test Report
        uses: actions/upload-artifact@v2
        with:
          name: test-report
          path: tests/reports/test-reports/
```

### 4. 品質閘門 (Quality Gate)

```bash
# PR merge 前自動檢查
*full-cycle

Sentinel:
  📊 品質檢查:
  - 單元測試通過率: 100% ✅ (需求 95%)
  - 整合測試通過率: 100% ✅ (需求 90%)
  - E2E 測試通過率: 100% ✅ (需求 80%)
  - 核心邏輯覆蓋率: 92% ✅ (需求 90%)
  - 高風險區域覆蓋率: 87% ✅ (需求 85%)
  
  🎉 所有品質閘門通過！PR 可以 merge
```

---

## 📋 命令速查表

| 命令 | 用途 | 耗時 | 產出報告 |
|------|------|------|----------|
| `*init` | 首次初始化 | 30s | ❌ |
| `*quick-test` | 快速測試變更 | 10-20s | ❌ |
| `*full-cycle` | **完整測試** | 2-5min | ✅ |
| `*scan-project` | 掃描專案結構 | 15s | ❌ |
| `*risk-map` | 產生風險地圖 | 20s | ✅ |
| `*quality-report` | 品質分析報告 | 30s | ✅ |

---

## ❓ 常見問題

### Q1: 我只想執行一次完整測試，該用哪個命令？

**A:** `*full-cycle` - 這就是你要的！

```bash
*full-cycle
# 自動完成：測試計畫 → 單元測試 → 整合測試 → E2E → 報告
```

### Q2: *full-cycle 會自動生成測試嗎？

**A:** 是的！Sentinel 會：
1. 掃描代碼
2. 自動生成測試案例
3. 執行所有測試
4. 產出完整報告

**你不需要手動寫任何測試！**

### Q3: 如果測試失敗怎麼辦？

**A:** Sentinel 會互動式處理：
- 顯示失敗原因
- 提供修復建議
- 詢問你要如何處理（自動修復/跳過/中斷）

### Q4: 我可以在 CI/CD 中使用嗎？

**A:** 完全可以！只需：
```yaml
# CI 配置中
- run: sentinel *full-cycle
```

Sentinel 會自動讀取 `.sentinel-config.yaml` 並執行。

### Q5: 報告在哪裡？

**A:** 測試完成後會顯示路徑：
```
📋 測試報告:
→ tests/reports/test-reports/TR-20260206-001.md
```

也可以查看：
- `tests/reports/test-reports/` - 測試報告
- `tests/reports/risk-maps/` - 風險地圖
- `tests/reports/quality-reports/` - 品質報告

---

## 🎯 總結

### 記住這一個命令

```bash
*full-cycle
```

**這就是你需要的！**

- ✅ 自動生成測試
- ✅ 執行所有測試
- ✅ 產出完整報告
- ✅ 測試失敗自動協助
- ✅ 品質閘門檢查

### 完美工作流

```
開發代碼 → 存檔 → *quick-test (快速驗證)
                        ↓
                    繼續開發
                        ↓
               功能完成 → *full-cycle (完整測試)
                        ↓
                  查看報告 → Commit → PR
```

---

**版本:** 1.0.0  
**維護者:** Sentinel Agent  
**最後更新:** 2026-02-06

🛡️ **一鍵測試，守護品質，解放雙手！**
