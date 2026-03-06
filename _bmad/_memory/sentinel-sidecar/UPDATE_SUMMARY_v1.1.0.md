# Sentinel Agent 更新摘要 - 通用化專案初始化

**日期:** 2026-02-06  
**版本:** 1.0.0 → 1.1.0  
**更新類型:** 重大功能增強 (Major Feature)

---

## 📋 更新概述

根據用戶反饋「不應寫死專案配置，應該做為流程的一開始」，將 Sentinel Agent 從**專案特定代理**升級為**通用測試代理**，支援任何專案自動初始化。

### 核心理念變更

**之前 (v1.0.0):**
```
❌ 綁定特定專案 (AuraTrade)
❌ 配置檔寫死在代碼中
❌ 無法用於其他專案
```

**現在 (v1.1.0):**
```
✅ 通用測試代理 (支援所有專案)
✅ 首次啟動自動檢測專案
✅ 動態生成配置檔
✅ 支援多專案切換
```

---

## 🎯 新增功能

### 1. 自動專案初始化 (Project Initialization)

**觸發時機:**
- 首次啟動 Sentinel
- 手動執行 `*init` 命令
- 專案根目錄缺少 `.sentinel-config.yaml`

**工作流程:**

#### 階段 1: 專案檢測
```yaml
自動掃描:
  - package.json → Node.js 專案
  - requirements.txt → Python 專案
  - go.mod → Go 專案
  - Cargo.toml → Rust 專案
  
檢測內容:
  - 專案類型 (frontend/backend/fullstack/monorepo)
  - 技術棧 (React/Vue/FastAPI/Express)
  - 測試框架 (Jest/Vitest/Pytest/Playwright)
  - 目錄結構與命名慣例
```

#### 階段 2: 互動式配置
```
🔍 自動檢測結果:

專案資訊:
  📁 專案名稱: AuraTrade
  📦 專案類型: Fullstack
  ⚛️  前端: React + TypeScript
  🐍 後端: Python + FastAPI

確認以上資訊正確? [Y/n]

📊 測試策略配置:
  [A] 標準配置: 60% 單元 / 30% 整合 / 10% E2E (推薦)
  [B] 高覆蓋配置: 50% / 35% / 15%
  [C] 敏捷配置: 70% / 20% / 10%
  選擇: [A]
```

#### 階段 3: 配置檔生成
```yaml
# 自動生成 .sentinel-config.yaml
project:
  name: "AuraTrade"
  version: "1.2.0"
  type: "fullstack"

tech_stack:
  frontend:
    framework: "React"
    test_framework: "Vitest"
  
  backend:
    framework: "FastAPI"
    test_framework: "Pytest"

test_strategy:
  pyramid_ratio: [60, 30, 10]
  coverage_target:
    core_logic: 90
    general_features: 80
```

#### 階段 4: 測試目錄建立
```
自動建立:
  tests/
  ├── unit/
  ├── integration/
  ├── e2e/
  ├── reports/
  └── mocks/
```

#### 階段 5: 初始掃描
```
📊 專案掃描結果:
   - 總檔案數: 156
   - 已測試: 23 (14.7%)
   - 未測試: 133 (85.3%)
   - 高風險檔案: 8

🔴 高風險檔案:
   1. src/services/payment.ts (Complexity: 15)
   2. src/services/trading.ts (Complexity: 16)
```

### 2. 重新初始化 (Reinit)

**命令:** `*reinit`

**用途:** 專案結構變更時更新配置

**流程:**
```yaml
1. 備份現有配置:
   .sentinel-config.yaml → .sentinel-config.yaml.bak

2. 詢問保留項目:
   - 保留測試策略? [Y/n]
   - 保留優先模組清單? [Y/n]

3. 重新掃描專案

4. 合併舊配置 + 新檢測結果

5. 產出更新配置檔
```

### 3. 多專案支援 (Multi-Project Support)

**自動切換:**
```bash
cd /path/to/ProjectA
*scan-project  # 自動載入 ProjectA 配置

cd /path/to/ProjectB
*init  # 若未初始化則自動執行初始化
```

**記憶隔離:**
```yaml
_bmad/_memory/sentinel-sidecar/memories.md:
  projects:
    - name: "AuraTrade"
      learning_data: {...}
    
    - name: "ProjectB"
      learning_data: {...}
```

---

## 📁 新增檔案

### 1. project-initialization.md
**位置:** `_bmad/_memory/sentinel-sidecar/workflows/project-initialization.md`

**內容:** 完整的專案初始化工作流，包含：
- 6 個階段詳細步驟
- 專案檢測邏輯 (支援多種語言/框架)
- 互動式配置流程
- 錯誤處理與常見問題
- 多專案支援機制
- 使用範例 (3 種情境)

**檔案大小:** ~15KB

### 2. config-template.md
**位置:** `_bmad/_memory/sentinel-sidecar/config-template.md`

**內容:** 配置檔範本與說明，包含：
- 基本配置範本 (完整 YAML)
- 純前端專案範本
- 純後端專案範本
- Monorepo 專案範本
- 配置檔使用流程
- 驗證規則
- 本機覆寫配置說明 (.sentinel-config.local.yaml)

**檔案大小:** ~8KB

### 3. QUICK_START.md
**位置:** `_bmad/_memory/sentinel-sidecar/QUICK_START.md`

**內容:** 快速入門指南，包含：
- 3 分鐘上手流程
- 常用命令速查表
- 4 個實際使用範例
- 常見問題 Q&A
- 進階使用技巧
- 學習路徑 (3 個級別)

**檔案大小:** ~12KB

---

## 🔧 檔案修改

### sentinel.agent.yaml

**修改位置 1: critical_actions**
```yaml
critical_actions:
  # === 新增: 專案初始化邏輯 ===
  - 'IF .sentinel-config.yaml NOT EXISTS: AUTO-EXECUTE initialization'
  - 'IF .sentinel-config.yaml EXISTS: LOAD config and skip init'
  
  # === 新增: 載入配置檔 (最先執行) ===
  - 'Load COMPLETE file {project-root}/.sentinel-config.yaml'
  
  # === 新增: 載入初始化工作流 ===
  - 'Load COMPLETE file .../workflows/project-initialization.md'
  
  # === 修改: 路徑使用配置檔定義 ===
  - 'ALL paths must use project.root from .sentinel-config.yaml'
```

**修改位置 2: prompts**
```yaml
prompts:
  # === 新增: 初始化命令 ===
  - id: init
    content: |
      執行 project-initialization.md 完整流程
      包含: 專案檢測 → 互動配置 → 生成配置檔 → 建立目錄 → 初始掃描

  # === 新增: 重新初始化命令 ===
  - id: reinit
    content: |
      備份舊配置 → 重新掃描 → 合併配置 → 更新檔案
```

**修改位置 3: menu**
```yaml
menu:
  # === 新增: 初始化命令選單 ===
  - trigger: INIT or fuzzy match on init
    action: '#init'
    description: '[INIT] 專案初始化：自動檢測並生成配置檔'
  
  - trigger: REINIT or fuzzy match on reinit
    action: '#reinit'
    description: '[REINIT] 重新初始化：更新專案配置'
```

---

## 🎯 使用流程變更

### 之前的流程 (v1.0.0)

```
1. 開發者: (啟動 Sentinel)
2. Sentinel: (載入預設配置)
3. 開發者: *scan-project
4. Sentinel: (掃描專案...)
```

**問題:**
- ❌ 配置寫死,無法用於其他專案
- ❌ 每次都要掃描
- ❌ 無法持久化專案配置

### 現在的流程 (v1.1.0)

```
1. 開發者: (首次啟動 Sentinel)
2. Sentinel: 🔍 檢測到尚未初始化
            開始自動檢測專案結構...
            [顯示檢測結果並詢問確認]
3. 開發者: Y (確認)
4. Sentinel: ✅ 配置檔已生成: .sentinel-config.yaml
            ✅ 測試目錄已建立: tests/
            ✅ 初始掃描完成
5. 開發者: (後續啟動 Sentinel)
6. Sentinel: 📂 載入專案配置: AuraTrade
            (直接使用已有配置,跳過掃描)
```

**優勢:**
- ✅ 只需初始化一次
- ✅ 配置可納入 Git 版本控制 (團隊共享)
- ✅ 支援任何專案
- ✅ 可手動調整配置檔

---

## 📊 支援的專案類型

### 前端專案
```
✅ React (TypeScript/JavaScript)
✅ Vue (Vite/CLI)
✅ Angular
✅ Svelte
✅ Next.js / Nuxt.js

測試框架:
✅ Vitest
✅ Jest
✅ @testing-library/react
✅ Playwright
✅ Cypress
```

### 後端專案
```
✅ Python (FastAPI/Flask/Django)
✅ Node.js (Express/Koa/NestJS)
✅ Go (Gin/Echo/Fiber)
✅ Rust (Actix/Rocket)

測試框架:
✅ Pytest
✅ unittest
✅ Jest
✅ Mocha
✅ Go testing
```

### 全棧專案
```
✅ 自動識別前後端分離
✅ 分別配置測試策略
✅ 整合測試支援
```

### Monorepo
```
✅ 多 workspace 支援
✅ 各 workspace 獨立配置
✅ 共享測試工具
```

---

## 🔄 向後相容性

### 現有專案遷移

**情境:** 已有 Sentinel v1.0.0 的專案

**步驟:**
```bash
1. 更新 Sentinel 到 v1.1.0

2. 執行初始化:
   *init

3. Sentinel 詢問:
   ⚠️  偵測到現有測試目錄: tests/
   
   選項:
   [A] 保留現有目錄,只生成配置檔
   [B] 合併現有測試到 Sentinel 結構
   [C] 取消初始化

4. 選擇 [A]:
   ✅ 保留現有 tests/ 目錄
   ✅ 生成 .sentinel-config.yaml
   
5. 後續使用:
   所有功能正常運作,無破壞性變更
```

**向後相容保證:**
- ✅ 現有測試目錄不受影響
- ✅ 測試報告格式不變
- ✅ 命令功能完全相同
- ✅ 記憶檔案自動遷移

---

## 💡 最佳實踐

### 1. 配置檔版本控制

```bash
# .gitignore
.sentinel-config.yaml.bak      # 備份檔案不追蹤
.sentinel-config.local.yaml    # 本機配置不追蹤

# Git 追蹤
.sentinel-config.yaml           # 主配置檔 (團隊共享)
```

### 2. 團隊協作

```yaml
# 團隊成員 A 初始化專案
*init
git add .sentinel-config.yaml
git commit -m "chore: add Sentinel config"
git push

# 團隊成員 B 拉取專案
git pull
(啟動 Sentinel)
# Sentinel 自動載入團隊配置,無需重複初始化
```

### 3. 本機客製化

```yaml
# .sentinel-config.local.yaml (不納入 Git)
test_strategy:
  coverage_target:
    general_features: 70  # 本機開發降低標準

tech_stack:
  database:
    - type: "SQLite"  # 本機用輕量資料庫
```

### 4. CI/CD 整合

```yaml
# .github/workflows/test.yml
- name: Verify Sentinel Config
  run: |
    if [ ! -f .sentinel-config.yaml ]; then
      echo "Error: Missing Sentinel config"
      exit 1
    fi

- name: Run Sentinel Tests
  run: |
    # Sentinel 自動讀取 .sentinel-config.yaml
    npm run test:all
```

---

## 🐛 已知限制

### 1. 專案檢測限制
```
⚠️  無法檢測:
   - 自訂專案結構 (非標準目錄)
   - 混合多種框架 (罕見情況)
   
💡 解決方案:
   手動編輯 .sentinel-config.yaml
```

### 2. 測試框架相依性
```
⚠️  若測試框架未安裝:
   Sentinel 會詢問是否自動安裝
   
💡 建議:
   先手動安裝測試框架,再執行 *init
```

### 3. Monorepo 複雜度
```
⚠️  Monorepo 每個 workspace 需獨立配置
   
💡 規劃中:
   v1.2.0 將支援單一配置檔管理多 workspace
```

---

## 📈 升級建議

### 誰應該升級？

✅ **立即升級:**
- 管理多個專案的團隊
- 需要在不同專案間切換
- 團隊協作需要共享配置

⏳ **觀望升級:**
- 只有單一專案且不需要切換
- 已有穩定的 v1.0.0 配置運作良好

### 升級步驟

```bash
# 1. 備份現有配置 (若有)
cp -r _bmad/_memory/sentinel-sidecar _bmad/_memory/sentinel-sidecar.bak

# 2. 更新 Sentinel Agent
(替換 sentinel.agent.yaml 等檔案)

# 3. 執行初始化
*init

# 4. 驗證配置
cat .sentinel-config.yaml

# 5. 執行測試週期驗證
*full-cycle

# 6. 確認無誤後刪除備份
rm -rf _bmad/_memory/sentinel-sidecar.bak
```

---

## 📞 回饋與支援

### 已實現的用戶反饋

✅ **原始需求 (2026-02-06):**
> "專案配置檔這部分,因為我不是專門只做本專案的專用代理,
> 因此我建議不要寫死,可以做為流程的一開始,
> 就是去檢查專案架構,並且先生出對應的配置檔案、
> 測試所需求的路徑如test資料夾之類的"

✅ **實現方式:**
- 首次啟動自動檢測專案
- 動態生成 .sentinel-config.yaml
- 自動建立 tests/ 目錄結構
- 支援多專案切換

✅ **額外實現:**
- 重新初始化功能 (*reinit)
- 本機覆寫配置 (.sentinel-config.local.yaml)
- 完整的快速入門指南 (QUICK_START.md)
- 多種專案類型範本

---

## 🎉 總結

### 更新亮點

1. **通用化設計** - 從專案特定代理升級為通用測試代理
2. **零配置啟動** - 首次使用自動檢測並生成配置
3. **多專案支援** - 輕鬆在不同專案間切換
4. **團隊協作** - 配置檔可納入 Git 版本控制
5. **完整文件** - 快速入門指南與詳細範例

### 檔案清單

**新增:**
- `workflows/project-initialization.md` (15KB)
- `config-template.md` (8KB)
- `QUICK_START.md` (12KB)

**修改:**
- `sentinel.agent.yaml` (+60 lines)

**總計:** +35KB 文件, 3 個新工作流

### 下一步規劃

**v1.2.0 (計畫中):**
- Monorepo 單一配置檔支援
- 配置檔視覺化編輯器
- 自動偵測專案依賴變更
- 團隊配置檔範本庫

---

**更新日期:** 2026-02-06  
**負責人:** Sentinel Agent  
**版本:** v1.1.0  
**相容性:** 完全向後相容 v1.0.0

🛡️ **Sentinel - 從專用代理到通用測試守護者**
