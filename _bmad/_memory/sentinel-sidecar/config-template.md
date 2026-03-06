# Sentinel 專案配置檔模板

此檔案為 Sentinel Agent 的專案配置範本，初始化時會自動生成。

---

## 基本配置範本

```yaml
---
# Sentinel Agent 專案配置
# 此檔案由 Sentinel 自動生成，可手動編輯
# 應納入 Git 版本控制 (團隊共享)

project:
  name: "MyProject"           # 專案名稱
  version: "1.0.0"            # 專案版本
  type: "fullstack"           # frontend | backend | fullstack | monorepo
  root: "/path/to/project"    # 專案根目錄

tech_stack:
  frontend:
    framework: "React"        # React | Vue | Angular | Svelte
    version: "18.2.0"
    language: "TypeScript"    # TypeScript | JavaScript
    source_dir: "src/"
    test_framework: "Vitest"  # Vitest | Jest | @testing-library/react
    test_runner: "vitest"
    package_manager: "npm"    # npm | yarn | pnpm
  
  backend:
    framework: "FastAPI"      # FastAPI | Flask | Django | Express | NestJS
    version: "0.109.0"
    language: "Python"        # Python | JavaScript | TypeScript | Go
    python_version: "3.11"    # 若為 Python 專案
    source_dir: "backend/"
    test_framework: "Pytest"  # Pytest | unittest | Jest | Mocha
    test_runner: "pytest"
    package_manager: "pip"    # pip | poetry | npm | yarn
  
  database:
    - type: "PostgreSQL"
      detected_from: "docker-compose.yml"
    - type: "Redis"
      detected_from: "docker-compose.yml"
  
  e2e:
    framework: "Playwright"   # Playwright | Cypress | Puppeteer
    installed: true
    browsers: ["chromium"]    # chromium | firefox | webkit

test_strategy:
  pyramid_ratio: [60, 30, 10]  # [Unit, Integration, E2E] 百分比
  
  coverage_target:
    core_logic: 90            # 核心邏輯覆蓋率目標
    general_features: 80      # 一般功能覆蓋率目標
    utils: 85                 # 工具函數覆蓋率目標
  
  priority_modules:           # 高優先級模組 (手動填入)
    - "src/services/payment.ts"
    - "src/auth/"
    - "backend/apps/api/"
  
  naming_conventions:
    test_file_suffix: ".test.ts"  # 測試檔案後綴
    test_naming_pattern: "should_ExpectedBehavior_When_StateUnderTest"

directory_structure:
  source:
    frontend: "src/"
    backend: "backend/"
  
  tests: "tests/"             # Sentinel 標準測試目錄
  output: "_bmad-output/"     # BMAD 輸出目錄

risk_profile:
  high_complexity_threshold: 15  # 高複雜度門檻
  
  critical_patterns:          # 關鍵字模式 (自動識別高風險)
    - "payment"
    - "auth"
    - "security"
    - "transaction"
  
  min_coverage:
    critical_files: 95        # Critical 檔案最低覆蓋率
    high_risk_files: 85       # High Risk 檔案最低覆蓋率

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

# 自訂配置 (選填)
custom:
  # 開發者可在此加入專案特定配置
  ci_cd_platform: "GitHub Actions"
  notification_webhook: null
  slack_channel: null
```

---

## 純前端專案範本

```yaml
---
project:
  name: "FrontendApp"
  type: "frontend"
  
tech_stack:
  frontend:
    framework: "React"
    language: "TypeScript"
    source_dir: "src/"
    test_framework: "Vitest"
    test_runner: "vitest"
  
  # 無 backend 區塊
  
  e2e:
    framework: "Playwright"
    browsers: ["chromium", "firefox"]

test_strategy:
  pyramid_ratio: [70, 20, 10]  # 前端專案單元測試比例更高
  
  coverage_target:
    components: 85
    hooks: 90
    utils: 90

directory_structure:
  source:
    frontend: "src/"
  tests: "tests/"
```

---

## 純後端專案範本

```yaml
---
project:
  name: "BackendAPI"
  type: "backend"

tech_stack:
  # 無 frontend 區塊
  
  backend:
    framework: "FastAPI"
    language: "Python"
    source_dir: "src/"
    test_framework: "Pytest"
  
  database:
    - type: "PostgreSQL"

test_strategy:
  pyramid_ratio: [60, 40, 0]  # 後端 API 無 E2E (或用 API 測試)
  
  coverage_target:
    api_routes: 95
    services: 90
    utils: 85

directory_structure:
  source:
    backend: "src/"
  tests: "tests/"
```

---

## Monorepo 專案範本

```yaml
---
project:
  name: "MonorepoProject"
  type: "monorepo"

tech_stack:
  workspaces:
    - name: "frontend"
      path: "apps/web/"
      framework: "React"
      test_framework: "Vitest"
    
    - name: "backend"
      path: "apps/api/"
      framework: "NestJS"
      test_framework: "Jest"
    
    - name: "shared"
      path: "packages/shared/"
      language: "TypeScript"
      test_framework: "Vitest"

test_strategy:
  per_workspace: true  # 每個 workspace 獨立測試策略

directory_structure:
  workspaces:
    - "apps/web/"
    - "apps/api/"
    - "packages/shared/"
  
  tests: "tests/"  # 全局測試 (或各 workspace 有自己的 tests/)
```

---

## 配置檔位置

```
專案根目錄/
├── .sentinel-config.yaml    ← 主配置檔 (Git tracked)
├── .sentinel-config.local.yaml  ← 本機覆寫配置 (Git ignored, 選用)
├── tests/
└── _bmad/
    └── _memory/
        └── sentinel-sidecar/
            └── memories.md  ← 持久化記憶 (從配置檔讀取專案資訊)
```

---

## 配置檔使用流程

```
1. 初始化時
   → Sentinel 掃描專案
   → 自動生成 .sentinel-config.yaml
   → 寫入檢測到的資訊

2. 首次執行測試
   → 載入 .sentinel-config.yaml
   → 更新 last_execution 區塊
   → 儲存最新結果

3. 後續執行
   → 讀取配置檔
   → 跳過重複掃描
   → 直接使用已知配置

4. 開發者手動調整
   → 編輯 .sentinel-config.yaml
   → Sentinel 下次執行時使用新配置
   → 不需要重新初始化
```

---

## 配置檔驗證規則

```yaml
必要欄位:
  - project.name
  - project.type
  - tech_stack (至少一個: frontend / backend)
  - test_strategy.pyramid_ratio
  - directory_structure.tests

可選欄位:
  - priority_modules
  - custom.*
  - last_execution.*

格式驗證:
  - pyramid_ratio 總和必須為 100
  - coverage_target 值必須在 0-100 之間
  - 所有路徑必須相對於 project.root
```

---

## 本機覆寫配置 (選用)

若需要本機特定配置 (例如不同的測試資料庫):

```yaml
# .sentinel-config.local.yaml (Git ignored)
---
tech_stack:
  database:
    - type: "SQLite"  # 本機開發用
      connection: "sqlite:///./test.db"

test_strategy:
  coverage_target:
    core_logic: 70  # 本機降低標準加速開發

# 其他欄位從 .sentinel-config.yaml 繼承
```

載入順序:
1. 載入 `.sentinel-config.yaml`
2. 若存在 `.sentinel-config.local.yaml`，覆寫對應欄位
3. 合併後的配置用於執行

---

**維護者:** Sentinel Agent  
**版本:** 1.0.0  
**最後更新:** 2026-02-06
