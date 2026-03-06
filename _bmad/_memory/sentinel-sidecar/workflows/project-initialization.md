# 專案初始化工作流 (Project Initialization)

**目標：** Sentinel 首次使用時自動檢測專案結構並生成配置

---

## 工作流觸發

**命令：** `*init` 或 `[INIT]` 或**首次啟動時自動執行**

**觸發條件：**
```yaml
自動觸發:
  - 檔案不存在: .sentinel-config.yaml
  - 目錄不存在: tests/

手動觸發:
  - 開發者執行: *init
  - 開發者執行: *reinit (重新初始化)
```

---

## 階段 1: 專案檢測 (Project Detection)

### 1.1 檢測專案類型

```yaml
檢測策略:
  1. 掃描根目錄檔案:
     - package.json → Node.js 專案
     - requirements.txt / pyproject.toml → Python 專案
     - go.mod → Go 專案
     - Cargo.toml → Rust 專案
     - pom.xml → Java 專案
  
  2. 判斷專案類型:
     - Frontend-only: 只有 src/ 或 public/
     - Backend-only: 只有 backend/ 或 api/
     - Fullstack: 同時存在前後端目錄
     - Monorepo: 存在 packages/ 或 apps/

範例輸出:
  專案類型: Fullstack
  前端: src/ (React + TypeScript)
  後端: backend/ (Python + FastAPI)
```

### 1.2 檢測技術棧

```yaml
前端檢測:
  掃描 package.json dependencies:
    - react → React
    - vue → Vue
    - angular → Angular
    - svelte → Svelte
  
  語言檢測:
    - tsconfig.json → TypeScript
    - jsconfig.json → JavaScript

後端檢測:
  Python:
    - fastapi / flask / django → Framework
    - 掃描 requirements.txt
  
  Node.js:
    - express / koa / nestjs → Framework
    - 掃描 package.json
  
  Go:
    - 掃描 go.mod
    - 檢測 gin / echo / fiber

資料庫檢測:
  掃描 docker-compose.yml:
    - postgres / mysql / mongodb
  
  掃描連線配置:
    - .env 檔案
    - config.yaml
```

### 1.3 檢測測試框架

```yaml
前端測試框架:
  檢查 package.json devDependencies:
    - jest → Jest
    - vitest → Vitest
    - @testing-library/react → React Testing Library
    - @playwright/test → Playwright
    - cypress → Cypress

後端測試框架:
  Python:
    - pytest → Pytest
    - unittest → unittest
  
  Node.js:
    - jest → Jest
    - mocha → Mocha
  
  若未安裝:
    → 詢問開發者偏好
    → 自動安裝推薦框架
```

### 1.4 檢測目錄結構

```yaml
掃描關鍵目錄:
  - src/ source/ app/ → 原始碼目錄
  - backend/ api/ server/ → 後端目錄
  - frontend/ client/ → 前端目錄
  - tests/ test/ __tests__/ → 測試目錄 (若存在)
  - docs/ → 文件目錄

識別命名慣例:
  - 檔案命名: camelCase / kebab-case / snake_case
  - 測試檔案後綴: .test.ts / .spec.ts / _test.py
```

---

## 階段 2: 互動式配置 (Interactive Configuration)

### 2.1 展示檢測結果

```
🛡️ Sentinel 專案初始化

🔍 自動檢測結果:

專案資訊:
  📁 專案名稱: AuraTrade (從 package.json 讀取)
  📦 專案類型: Fullstack
  📂 根目錄: C:\Users\coolc\AuraTrade

前端:
  ⚛️  框架: React 18.2.0
  📘 語言: TypeScript
  🧪 測試框架: Vitest ✅ (已安裝)
  📂 原始碼: src/

後端:
  🐍 語言: Python 3.11
  ⚡ 框架: FastAPI 0.109.0
  🧪 測試框架: Pytest ✅ (已安裝)
  📂 原始碼: backend/

資料庫:
  🐘 PostgreSQL (從 docker-compose.yml 檢測)
  🔴 Redis (從 docker-compose.yml 檢測)

E2E:
  🎭 Playwright ⚠️ (未安裝)

確認以上資訊正確? [Y/n]
```

### 2.2 詢問測試策略

```
📊 測試策略配置

1. 測試金字塔比例:
   [A] 標準配置: 60% 單元 / 30% 整合 / 10% E2E (推薦)
   [B] 高覆蓋配置: 50% 單元 / 35% 整合 / 15% E2E
   [C] 敏捷配置: 70% 單元 / 20% 整合 / 10% E2E
   [D] 自訂比例
   
   選擇: [A/B/C/D] (預設 A)

2. 覆蓋率目標:
   核心邏輯: __% (預設 90%)
   一般功能: __% (預設 80%)
   工具函數: __% (預設 85%)

3. 優先測試模組 (選填):
   請輸入高風險模組路徑 (用逗號分隔):
   範例: src/services/payment.ts, src/auth/, backend/apps/api/
   
   輸入: ___

4. 安裝缺少的測試框架?
   ⚠️  Playwright 未安裝,是否安裝? [Y/n]
```

---

## 階段 3: 配置檔生成 (Config Generation)

### 3.1 生成 .sentinel-config.yaml

```yaml
# 自動生成的配置檔
---
# Sentinel Agent 專案配置
# 生成日期: 2026-02-06T16:30:00+08:00
# 生成版本: Sentinel v1.0.0

project:
  name: "AuraTrade"  # 從 package.json 讀取
  version: "1.2.0"   # 從 package.json 讀取
  type: "fullstack"  # frontend | backend | fullstack | monorepo
  root: "C:\\Users\\coolc\\AuraTrade"

tech_stack:
  frontend:
    framework: "React"
    version: "18.2.0"
    language: "TypeScript"
    source_dir: "src/"
    test_framework: "Vitest"
    test_runner: "vitest"
    package_manager: "npm"  # npm | yarn | pnpm
  
  backend:
    framework: "FastAPI"
    version: "0.109.0"
    language: "Python"
    python_version: "3.11"
    source_dir: "backend/"
    test_framework: "Pytest"
    test_runner: "pytest"
    package_manager: "pip"
  
  database:
    - type: "PostgreSQL"
      detected_from: "docker-compose.yml"
    - type: "Redis"
      detected_from: "docker-compose.yml"
  
  e2e:
    framework: "Playwright"
    installed: true
    browsers: ["chromium"]  # 預設安裝 chromium

test_strategy:
  pyramid_ratio: [60, 30, 10]  # Unit:Integration:E2E
  
  coverage_target:
    core_logic: 90
    general_features: 80
    utils: 85
  
  priority_modules: []  # 開發者可後續填入
  
  naming_conventions:
    test_file_suffix: ".test.ts"  # 從現有測試檔案推斷
    test_naming_pattern: "should_ExpectedBehavior_When_StateUnderTest"

directory_structure:
  source:
    frontend: "src/"
    backend: "backend/"
  
  tests: "tests/"  # Sentinel 標準目錄
  
  output: "_bmad-output/"  # BMAD 輸出目錄

risk_profile:
  high_complexity_threshold: 15
  critical_patterns:
    - "payment"
    - "auth"
    - "security"
  
  min_coverage:
    critical_files: 95
    high_risk_files: 85

initialization:
  initialized_at: "2026-02-06T16:30:00+08:00"
  sentinel_version: "1.0.0"
  auto_generated: true

last_execution:
  test_plan_id: null
  test_report_id: null
  risk_map_id: null
  timestamp: null
  coverage: null
  pass_rate: null

# 開發者可手動編輯此檔案
# 此檔案應納入 Git 版本控制 (團隊共享配置)
```

**檔案位置:** `{project-root}/.sentinel-config.yaml`

### 3.2 生成 .gitignore 條目

```
自動檢查是否存在 .gitignore
若存在,詢問是否加入以下內容:

# Sentinel Agent
.sentinel-config.yaml.bak
_bmad/_memory/sentinel-sidecar/change-tracker.yaml
tests/unit/coverage/
tests/integration/coverage/
tests/e2e/screenshots/
tests/e2e/videos/
tests/reports/archives/
```

---

## 階段 4: 測試目錄建立 (Test Directory Setup)

### 4.1 建立標準目錄結構

```yaml
建立以下目錄:
  tests/
    ├── README.md (自動生成,包含專案特定資訊)
    ├── .gitignore
    ├── unit/
    │   ├── services/
    │   ├── utils/
    │   └── components/ (若為前端專案)
    ├── integration/
    │   ├── api/
    │   └── database/
    ├── e2e/
    │   ├── scenarios/
    │   └── fixtures/
    ├── reports/
    │   ├── test-plans/
    │   ├── test-reports/
    │   ├── risk-maps/
    │   └── quality-reports/
    └── mocks/
        ├── api-responses/
        └── database-seeds/

若目錄已存在:
  → 跳過建立
  → 警告: "tests/ 目錄已存在,跳過建立"
```

### 4.2 生成 tests/README.md

```markdown
# {ProjectName} 測試套件

**專案:** {ProjectName}  
**技術棧:** {Framework} + {TestFramework}  
**初始化日期:** {Date}  
**Sentinel 版本:** 1.0.0

---

## 🚀 快速開始

### 執行測試
\`\`\`bash
# 全部測試
npm test

# 單元測試
npm run test:unit

# 整合測試
npm run test:integration

# E2E 測試
npm run test:e2e
\`\`\`

### 使用 Sentinel
\`\`\`bash
# 完整測試週期
*full-cycle

# 掃描專案
*scan-project

# 生成測試
*generate-tests --file=src/services/payment.ts
\`\`\`

---

## 📁 目錄結構

[完整目錄結構說明...]

---

**此檔案由 Sentinel Agent 自動生成**  
**配置檔案:** .sentinel-config.yaml
```

### 4.3 生成測試配置檔

```yaml
根據專案類型生成:

前端 (Vitest):
  生成: vitest.config.ts (若不存在)
  配置: coverage, test directories, global setup

後端 (Pytest):
  生成: pytest.ini (若不存在)
  配置: testpaths, coverage, markers

E2E (Playwright):
  生成: playwright.config.ts (若不存在)
  配置: baseURL, browsers, screenshots
```

---

## 階段 5: 初始掃描 (Initial Scan)

### 5.1 執行專案掃描

```yaml
自動執行:
  1. 掃描所有原始碼檔案
  2. 計算代碼複雜度
  3. 識別未測試檔案
  4. 生成初始風險地圖

產出:
  - tests/reports/risk-maps/RM-INIT-001.md
  - 終端顯示掃描摘要
```

### 5.2 產出初始報告

```
🛡️ Sentinel 初始化完成!

✅ 配置檔案: .sentinel-config.yaml
✅ 測試目錄: tests/ (已建立)
✅ 初始掃描: 完成

📊 專案掃描結果:
   - 總檔案數: 156
   - 已測試: 23 (14.7%)
   - 未測試: 133 (85.3%)
   - 平均複雜度: 7.2
   - 高風險檔案: 8

🔴 高風險檔案 (建議優先測試):
   1. src/services/payment.ts (Complexity: 15, Coverage: 0%)
   2. src/services/trading.ts (Complexity: 16, Coverage: 0%)
   3. src/auth/validateToken.ts (Complexity: 12, Coverage: 0%)

📋 建議下一步:
   [1] 生成測試計畫: *test-strategy
   [2] 產生風險地圖: *risk-map
   [3] 自動生成測試: *generate-tests
   [4] 執行完整測試週期: *full-cycle

💡 提示: 配置檔案已儲存至 .sentinel-config.yaml
         你可以手動編輯此檔案調整測試策略
```

---

## 階段 6: 持久化記憶 (Memory Initialization)

### 6.1 初始化 memories.md

```yaml
在 _bmad/_memory/sentinel-sidecar/memories.md 寫入:
  - 專案基本資訊 (從配置檔讀取)
  - 初始化時間戳
  - 初始掃描結果
  - 空的學習區塊 (待 AI 填充)
```

### 6.2 建立 change-tracker.yaml

```yaml
建立空的變更追蹤檔:
  last_scan:
    timestamp: "2026-02-06T16:30:00+08:00"
    commit_hash: "{current_git_hash}"
  
  file_checksums: {}
  dependency_graph: {}
  change_history: []
```

---

## 錯誤處理

### 常見錯誤

#### 錯誤 1: 無法識別專案類型
```yaml
症狀:
  - 缺少 package.json / requirements.txt 等關鍵檔案
  
解決方案:
  1. 詢問開發者手動指定專案類型
  2. 提供互動式配置選單
  3. 生成最小化配置檔
```

#### 錯誤 2: 測試框架未安裝
```yaml
症狀:
  - 無法檢測到 jest / pytest 等
  
解決方案:
  1. 詢問是否自動安裝
  2. 提供安裝命令建議
  3. 允許稍後手動配置
```

#### 錯誤 3: 權限不足
```yaml
症狀:
  - 無法建立 tests/ 目錄
  - 無法寫入配置檔
  
解決方案:
  1. 檢查目錄權限
  2. 建議使用 sudo (Linux/Mac)
  3. 建議以管理員身份執行 (Windows)
```

---

## 重新初始化 (Reinit)

### 觸發條件
```
開發者執行: *reinit
```

### 處理流程
```yaml
1. 備份現有配置:
   cp .sentinel-config.yaml .sentinel-config.yaml.bak

2. 詢問保留項目:
   - 保留測試策略? [Y/n]
   - 保留優先模組清單? [Y/n]
   - 保留測試歷史? [Y/n]

3. 重新掃描專案

4. 合併舊配置 + 新檢測結果

5. 產出更新後的配置檔
```

---

## 多專案支援

### 專案切換
```yaml
Sentinel 可同時管理多個專案:
  - 每個專案有獨立的 .sentinel-config.yaml
  - 記憶檔案共用但隔離 (依 project.name 區分)
  - 自動檢測當前工作目錄

切換邏輯:
  1. 檢查當前目錄是否有 .sentinel-config.yaml
  2. 若有 → 載入該專案配置
  3. 若無 → 觸發初始化流程
```

### 記憶隔離
```yaml
_bmad/_memory/sentinel-sidecar/memories.md:
  projects:
    - name: "AuraTrade"
      learning_data: {...}
    
    - name: "ProjectB"
      learning_data: {...}

載入時:
  根據 .sentinel-config.yaml 中的 project.name
  載入對應的 learning_data
```

---

## 使用範例

### 範例 1: 全新專案
```
開發者: (首次啟動 Sentinel)

Sentinel:
  🛡️ 歡迎使用 Sentinel Agent!
  
  🔍 檢測到你尚未初始化此專案
  
  開始自動檢測專案結構...
  ✅ 檢測完成 (3.2 秒)
  
  [顯示檢測結果...]
  
  確認以上資訊正確? [Y/n]

開發者: Y

Sentinel:
  📊 測試策略配置...
  [互動式配置...]
  
  ✅ 配置檔案已生成: .sentinel-config.yaml
  ✅ 測試目錄已建立: tests/
  ✅ 初始掃描完成
  
  [顯示掃描結果與建議...]
```

### 範例 2: 現有測試專案
```
開發者: (專案已有 tests/ 目錄)

Sentinel:
  🛡️ 歡迎使用 Sentinel Agent!
  
  🔍 檢測到你尚未初始化 Sentinel 配置
  
  ⚠️  偵測到現有測試目錄: tests/
  
  選項:
    [A] 保留現有目錄,只生成配置檔
    [B] 合併現有測試到 Sentinel 結構
    [C] 取消初始化
  
  選擇: [A/B/C]

開發者: A

Sentinel:
  ✅ 保留現有測試目錄
  ✅ 配置檔案已生成: .sentinel-config.yaml
  
  💡 提示: 你可以執行 *scan-project 掃描現有測試
```

### 範例 3: 專案遷移
```
開發者: 從專案 A 切換到專案 B

Sentinel:
  🔍 檢測到工作目錄變更
  
  上一個專案: AuraTrade
  當前專案: ProjectB
  
  🔍 掃描 ProjectB 配置...
  ⚠️  未找到 .sentinel-config.yaml
  
  是否初始化 ProjectB? [Y/n]

開發者: Y

Sentinel:
  [執行初始化流程...]
```

---

## 檢查清單

### 初始化完成檢查
- [ ] .sentinel-config.yaml 已生成
- [ ] tests/ 目錄結構已建立
- [ ] tests/README.md 包含專案特定資訊
- [ ] .gitignore 已更新 (若需要)
- [ ] 測試框架配置檔已生成 (若需要)
- [ ] memories.md 已初始化專案區塊
- [ ] change-tracker.yaml 已建立
- [ ] 初始風險地圖已產出
- [ ] 終端顯示建議下一步

### 品質檢查
- [ ] 配置檔格式正確 (YAML valid)
- [ ] 所有路徑使用絕對路徑或正確的相對路徑
- [ ] 檢測到的技術棧資訊正確
- [ ] 測試框架版本相容
- [ ] 目錄權限正確

---

**版本:** 1.0.0  
**維護者:** Sentinel Agent  
**最後更新:** 2026-02-06  
**適用範圍:** 所有支援的專案類型
