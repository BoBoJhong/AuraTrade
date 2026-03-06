# Sentinel Agent 快速入門指南

**適用對象:** 首次使用 Sentinel 或需要快速上手的開發者

---

## 🚀 第一次使用 (3 分鐘)

### 步驟 1: 自動初始化

```bash
# 在專案根目錄啟動 Sentinel
*init
```

**Sentinel 會自動:**
- 🔍 掃描專案結構 (檢測 React/Vue/Python/Node.js)
- 📦 識別測試框架 (Jest/Vitest/Pytest/Playwright)
- ⚙️ 生成配置檔 `.sentinel-config.yaml`
- 📁 建立測試目錄 `tests/`
- 📊 產出初始掃描報告

**互動確認:**
```
🔍 自動檢測結果:

專案資訊:
  📁 專案名稱: AuraTrade
  📦 專案類型: Fullstack
  ⚛️  前端: React + TypeScript
  🐍 後端: Python + FastAPI

確認以上資訊正確? [Y/n]
```

### 步驟 2: 檢視配置檔

```yaml
# .sentinel-config.yaml (已自動生成)
project:
  name: "AuraTrade"
  type: "fullstack"

tech_stack:
  frontend:
    framework: "React"
    test_framework: "Vitest"
  
  backend:
    framework: "FastAPI"
    test_framework: "Pytest"

# 可手動編輯調整測試策略
```

### 步驟 3: 執行第一個測試週期

```bash
# 完整測試流程
*full-cycle
```

**Sentinel 會依序執行:**
1. ✅ 生成測試計畫 → `tests/reports/test-plans/TP-20260206-001.md`
2. ✅ 執行單元測試 → `tests/unit/`
3. ✅ 執行整合測試 → `tests/integration/`
4. ✅ 執行 E2E 測試 → `tests/e2e/`
5. ✅ 產出測試報告 → `tests/reports/test-reports/TR-20260206-001.md`

---

## 📂 生成的目錄結構

```
專案根目錄/
├── .sentinel-config.yaml  ← 專案配置檔 (Git tracked)
├── tests/                  ← 測試目錄 (自動建立)
│   ├── README.md           ← 測試說明文件
│   ├── unit/               ← 單元測試
│   │   ├── services/
│   │   ├── utils/
│   │   └── components/
│   ├── integration/        ← 整合測試
│   │   ├── api/
│   │   └── database/
│   ├── e2e/                ← 端對端測試
│   │   ├── scenarios/
│   │   └── fixtures/
│   ├── reports/            ← 測試報告
│   │   ├── test-plans/
│   │   ├── test-reports/
│   │   ├── risk-maps/
│   │   └── quality-reports/
│   └── mocks/              ← Mock 資料
│       ├── api-responses/
│       └── database-seeds/
└── _bmad/
    └── _memory/
        └── sentinel-sidecar/  ← Sentinel 私有記憶區
```

---

## 🎯 常用命令速查

### 初始化與配置
```bash
*init       # 首次初始化專案
*reinit     # 重新初始化 (專案結構變更時)
```

### 掃描與分析
```bash
*scan-project  # 掃描專案代碼結構
*risk-map      # 產生風險地圖 (高複雜度區域)
*test-strategy # 建議測試策略
```

### 測試生成
```bash
*generate-tests --file=src/services/payment.ts  # 針對特定檔案
*generate-tests --module=src/auth/              # 針對整個模組
*generate-mocks                                 # 生成 Mock 資料
```

### 測試執行
```bash
*full-cycle     # 完整測試週期 (旗艦功能)
*quality-report # 產生品質報告
*fix-proposal   # 分析失敗測試並提供修復建議
```

### TDD 模式
```bash
*tdd-mode      # TDD 助手：先寫測試，再實現功能
```

---

## 💡 實際使用範例

### 範例 1: 全新專案建立測試

**情境:** 剛開始專案開發，想建立測試架構

```bash
# 步驟 1: 初始化
開發者: *init
Sentinel: [自動掃描並生成配置...]
          ✅ 配置檔案: .sentinel-config.yaml
          ✅ 測試目錄: tests/
          
          📊 專案掃描結果:
          - 總檔案數: 156
          - 未測試: 133 (85.3%)
          - 高風險檔案: 8
          
          🔴 高風險檔案:
          1. src/services/payment.ts (Complexity: 15)
          2. src/services/trading.ts (Complexity: 16)

# 步驟 2: 針對高風險檔案生成測試
開發者: *generate-tests --file=src/services/payment.ts
Sentinel: [生成 10 個測試案例...]
          ✅ tests/unit/services/payment.test.ts (已生成)
          
          📋 測試案例包含:
          - 正常流程: 3 個
          - 邊界條件: 4 個
          - 錯誤處理: 3 個

# 步驟 3: 執行測試
開發者: npm run test:unit
終端: ✅ 10/10 passed (100%)
```

### 範例 2: 現有專案加入 Sentinel

**情境:** 專案已有一些測試，想用 Sentinel 管理

```bash
開發者: *init
Sentinel: 🔍 檢測到現有測試目錄: tests/
          
          選項:
          [A] 保留現有目錄,只生成配置檔
          [B] 合併現有測試到 Sentinel 結構
          [C] 取消初始化
          
          選擇: [A/B/C]

開發者: A
Sentinel: ✅ 保留現有測試目錄
          ✅ 配置檔案已生成: .sentinel-config.yaml
          
          💡 提示: 執行 *scan-project 掃描現有測試

開發者: *scan-project
Sentinel: 📊 掃描結果:
          - 已測試檔案: 23 (14.7%)
          - 未測試檔案: 133 (85.3%)
          - 平均覆蓋率: 42%
          
          📋 建議下一步:
          [1] 生成風險地圖: *risk-map
          [2] 補強高風險區域: *generate-tests
```

### 範例 3: 定期品質檢查

**情境:** 每週執行品質檢查並產生報告

```bash
開發者: *quality-report
Sentinel: [分析所有測試結果...]
          
          📊 品質報告已產出:
          → tests/reports/quality-reports/QR-20260206-001.md
          
          📈 關鍵指標:
          - 整體覆蓋率: 87% (↑5% vs 上週)
          - 高風險區域: 3 個 (↓2 vs 上週)
          - 通過率: 97.5%
          
          ⚠️  優先行動:
          1. payment.ts: 複雜度 15, 覆蓋率 65%
          2. trading.ts: 複雜度 16, 覆蓋率 58%
```

### 範例 4: TDD 開發新功能

**情境:** 採用 TDD 方式開發新功能

```bash
# 步驟 1: 描述需求
開發者: *tdd-mode
        需求: 用戶可以設定股票價格提醒
        路徑: src/services/priceAlert.ts

Sentinel: [生成測試案例...]
          ✅ tests/unit/services/priceAlert.test.ts
          
          測試案例:
          ✅ should create price alert when valid input
          ✅ should reject negative price
          ✅ should reject duplicate alert
          ✅ should trigger notification when price reached
          
          空函數已生成:
          → src/services/priceAlert.ts
          
          💡 請填入實現代碼,然後執行測試

# 步驟 2: 開發者實現功能
開發者: (編寫 priceAlert.ts 實現代碼)

# 步驟 3: 執行測試
開發者: npm run test:unit priceAlert
終端: ✅ 4/4 passed

Sentinel: 🎉 所有測試通過! TDD 循環完成
```

---

## 🔧 常見問題

### Q1: 配置檔可以手動編輯嗎？
**A:** 可以！`.sentinel-config.yaml` 完全可手動編輯，例如：
```yaml
test_strategy:
  priority_modules:
    - "src/services/payment.ts"  # 手動加入高優先級模組
    - "src/auth/"
  
  coverage_target:
    core_logic: 95  # 調整覆蓋率目標
```

### Q2: 如何在多個專案間切換？
**A:** Sentinel 自動檢測！只要切換目錄即可：
```bash
cd /path/to/ProjectA
*scan-project  # 自動載入 ProjectA 配置

cd /path/to/ProjectB
*init  # 若未初始化則執行初始化
```

### Q3: 測試目錄已存在怎麼辦？
**A:** 初始化時 Sentinel 會詢問：
- **[A]** 保留現有目錄 → 只生成配置檔
- **[B]** 合併到 Sentinel 結構 → 自動重組

### Q4: 如何更新專案配置？
**A:** 當專案結構變更時：
```bash
*reinit  # 重新掃描並更新配置
```

### Q5: 配置檔該放入 Git 嗎？
**A:** 
- `.sentinel-config.yaml` → **應放入 Git** (團隊共享)
- `.sentinel-config.local.yaml` → **加入 .gitignore** (本機覆寫)

---

## 📚 進階使用

### 自訂測試策略

```yaml
# .sentinel-config.yaml
test_strategy:
  pyramid_ratio: [50, 35, 15]  # 調整測試金字塔比例
  
  coverage_target:
    critical_files: 98   # Critical 檔案要求更高
    high_risk_files: 90
    general_features: 75  # 一般功能降低標準
  
  priority_modules:
    - "src/services/payment.ts"  # 優先測試
    - "src/auth/"
    - "backend/apps/api/orders/"
```

### 本機覆寫配置

```yaml
# .sentinel-config.local.yaml (Git ignored)
tech_stack:
  database:
    - type: "SQLite"  # 本機開發用測試資料庫
      connection: "sqlite:///./test.db"

test_strategy:
  coverage_target:
    general_features: 60  # 本機降低標準加速開發
```

### CI/CD 整合

```yaml
# .github/workflows/test.yml
name: Sentinel Quality Gate

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Load Sentinel Config
        run: |
          # Sentinel 自動讀取 .sentinel-config.yaml
          
      - name: Run Full Test Cycle
        run: |
          npm install
          npm run test:all
          
      - name: Check Quality Thresholds
        run: |
          # Sentinel 自動驗證 coverage_target
          if [ coverage < threshold ]; then
            exit 1
          fi
```

---

## 🎓 學習路徑

### Level 1: 基礎使用 (第 1 週)
- [x] 執行 `*init` 初始化專案
- [x] 檢視生成的 `.sentinel-config.yaml`
- [x] 執行 `*scan-project` 掃描專案
- [x] 執行 `*generate-tests` 生成第一個測試

### Level 2: 進階功能 (第 2-3 週)
- [ ] 執行 `*full-cycle` 完整測試週期
- [ ] 使用 `*risk-map` 識別高風險區域
- [ ] 調整 `.sentinel-config.yaml` 測試策略
- [ ] 查看測試報告 `tests/reports/`

### Level 3: 專家級 (第 4 週+)
- [ ] 使用 `*tdd-mode` 進行 TDD 開發
- [ ] 定期執行 `*quality-report` 追蹤趨勢
- [ ] 建立 `.sentinel-config.local.yaml` 本機配置
- [ ] 整合 CI/CD 自動化品質守護

---

## 📞 獲取幫助

### 查看可用命令
```bash
# Sentinel 會顯示完整功能選單
(啟動 Sentinel 後即可看到)
```

### 查看詳細文件
```
_bmad/_memory/sentinel-sidecar/
├── workflows/
│   ├── full-test-cycle.md            ← 完整測試流程
│   ├── project-initialization.md     ← 初始化詳細說明
│   └── test-output-structure.md      ← 溯源編號系統
├── knowledge/
│   ├── testing-pyramid.md            ← 測試金字塔理論
│   ├── framework-references.md       ← 測試框架參考
│   └── best-practices.md             ← 最佳實踐
└── config-template.md                ← 配置檔範本
```

---

**版本:** 1.0.0  
**維護者:** Sentinel Agent  
**最後更新:** 2026-02-06

🛡️ **守護你的創造力，讓測試成為盟友而非負擔**
