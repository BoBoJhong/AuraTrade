# Sentinel Agent 可移植性分析報告

**評估日期:** 2026-02-11  
**評估專案:** AuraTrade  
**目標:** 使 Sentinel Agent 能快速部署到任意專案

---

## 📊 可移植性評分

**總體評分: 70/100** (可移植,需適配)

```yaml
評分細項:
  架構設計: 95/100  # ✅ 優秀 - 通用測試架構
  配置靈活性: 60/100  # ⚠️ 中等 - 部分硬編碼
  文檔完整性: 85/100  # ✅ 良好 - 有詳細工作流文檔
  自動化程度: 50/100  # ⚠️ 中等 - 需手動調整
  跨語言支持: 40/100  # ⚠️ 弱 - 僅支持 Python 完整
```

---

## ✅ 可直接復用部分 (30%)

### 1. 測試架構設計理念

```yaml
復用難度: ⭐️ (零成本)
適用範圍: 所有專案

包含:
  - 測試金字塔比例 (60% unit, 30% integration, 10% e2e)
  - 覆蓋率目標設定 (70% overall, 90% critical)
  - 風險識別策略 (關鍵字: auth, payment, security)
  - 優先級分類 (Critical > High > Medium)
```

### 2. 工作流框架

```yaml
復用難度: ⭐️ (零成本)
適用範圍: 所有 Web 應用

文件:
  - performance-testing.md (性能測試流程)
  - ci-automation.md (CI/CD 自動化流程)

可直接作為:
  - 團隊測試規範文檔
  - 新人 onboarding 教材
  - Code Review 檢查清單
```

### 3. 測試執行配置

```yaml
復用難度: ⭐️ (零成本)
適用範圍: 所有專案

包含:
  - parallel: true (並行執行)
  - timeout 設定 (30s unit, 60s integration)
  - retry_flaky: 2 (重試不穩定測試)
  - fail_fast: false (繼續執行所有測試)
```

---

## ⚠️ 需要調整部分 (40%)

### 1. 專案配置 (.sentinel-config.yaml)

```yaml
復用難度: ⭐️⭐️ (輕度調整)
調整時間: 5-10 分鐘

需要替換:
  project:
    name: "AuraTrade" → "YourProject"
    type: "fullstack" → "python|nodejs|java|..."
    root: "C:\\Users\\...\\AuraTrade" → 你的專案路徑
    description: "AI投資系統" → 你的專案描述

  tech_stack:
    backend.language: "Python" → 你的語言
    backend.framework: "FastAPI" → 你的框架
    backend.test_framework: "Pytest" → 你的測試框架
```

### 2. 優先模組標記 (priority_modules)

```yaml
復用難度: ⭐️⭐️⭐️ (中度調整)
調整時間: 30-60 分鐘

需要手動標記:
  AuraTrade 範例:
    critical:
      - AuthService (認證)
      - GeminiService (AI 核心)
      - TechnicalIndicatorService (計算核心)
  
  你的專案:
    critical:
      - [ ] 你的認證模組
      - [ ] 你的核心業務邏輯
      - [ ] 你的金融/支付模組 (如有)

建議:
  1. 找出涉及「錢」「密碼」「資料安全」的模組 → Critical
  2. 找出核心業務功能模組 → High
  3. 其他輔助功能 → Medium
```

### 3. 測試目錄結構 (test_directories)

```yaml
復用難度: ⭐️⭐️ (輕度調整)
調整時間: 5 分鐘

AuraTrade 結構:
  tests/
    ├── unit/
    ├── integration/
    ├── e2e/
    └── performance/

如果你的專案不同:
  - Django: tests/ 在 app/tests/ 下 → 調整 root
  - NestJS: test/ → 改為 test
  - Java: src/test/ → 改為 src/test
```

---

## 🔧 需要自訂部分 (30%)

### 1. 性能測試邏輯 (locustfile.py)

```yaml
復用難度: ⭐️⭐️⭐️⭐️ (高度自訂)
調整時間: 1-2 小時

AuraTrade 專用邏輯:
  - TEST_STOCKS = ["2330.TW", "AAPL", ...]  # 股票代碼
  - /api/v1/stocks/:symbol                 # API 路徑
  - /api/v1/auth/login                     # 認證端點

需要替換為:
  你的專案:
    - TEST_DATA = [你的測試數據]
    - /api/v1/your-endpoints
    - 你的業務場景任務 @task

模板提供:
  - 基礎結構 (HttpUser, task, between)
  - 通用場景 (Auth, CRUD, Search)
  - 你只需更換 API 路徑和測試數據
```

### 2. E2E 測試場景

```yaml
復用難度: ⭐️⭐️⭐️⭐️⭐️ (完全自訂)
調整時間: 4-8 小時

AuraTrade 場景:
  1. 用戶註冊登入
  2. 查詢股票 2330.TW
  3. 加入自選股
  4. 設定價格警報

你的專案:
  需要根據用戶流程完全自訂
  
建議:
  - 先列出 5 個核心用戶流程
  - 每個流程寫成一個 test scenario
  - 使用 Playwright Codegen 錄製操作
```

### 3. CI/CD Workflow

```yaml
復用難度: ⭐️⭐️⭐️ (中度自訂)
調整時間: 30-60 分鐘

可復用:
  - Job 結構 (8 個 jobs)
  - 品質閘門 (coverage ≥ 70%)
  - 並行策略

需要調整:
  - 專案路徑 (working-directory)
  - 依賴安裝命令 (pip/npm/maven)
  - 服務依賴 (PostgreSQL → MySQL?)
  - 環境變數 (secrets)
```

---

## 🚀 快速部署方案

### 方案 A: 初始化腳本 (推薦)

```powershell
# 1. 複製模板目錄
cp -r AuraTrade/_bmad/_templates/ YourProject/_bmad/_templates/

# 2. 執行初始化
cd YourProject
./_bmad/_templates/init-sentinel.ps1 `
  -ProjectName "YourProject" `
  -ProjectType "python" `
  -Description "你的專案描述"

# 3. 編輯自動生成的 .sentinel-config.yaml
# 填寫 priority_modules

# 4. 啟動 Sentinel
"啟動 Sentinel Agent"
```

預計時間: **15 分鐘**

### 方案 B: 手動配置

```bash
# 1. 創建配置文件
cp _bmad/_templates/sentinel-config.template.yaml .sentinel-config.yaml

# 2. 編輯配置 (替換 {{變數}})
vim .sentinel-config.yaml

# 3. 創建目錄結構
mkdir -p tests/{unit,integration,e2e,performance,reports}
mkdir -p _bmad/_memory/sentinel-sidecar

# 4. 複製 Locust 模板
cp _bmad/_templates/locustfile.template.py tests/performance/locustfile.py
vim tests/performance/locustfile.py  # 自訂 API 端點

# 5. 啟動 Sentinel
"啟動 Sentinel Agent"
```

預計時間: **30 分鐘**

---

## 🌍 跨專案類型支持

### Python (✅ 完整支持)

```yaml
支持程度: 95%
框架: FastAPI, Django, Flask
測試框架: Pytest, Unittest
性能測試: Locust
CI/CD: GitHub Actions ✅

需要調整:
  - 專案配置 (5 分鐘)
  - 優先模組 (30 分鐘)
  - 性能測試數據 (1 小時)
```

### Node.js/TypeScript (🟡 部分支持)

```yaml
支持程度: 60%
框架: Express, NestJS, React, Vue
測試框架: Jest, Vitest
性能測試: Locust (需要後端), Artillery (替代)
CI/CD: GitHub Actions ✅

需要調整:
  - 專案配置 (5 分鐘)
  - 測試框架適配 (2 小時) ⚠️
  - CI/CD workflow (30 分鐘)
```

### Java (🟡 實驗性支持)

```yaml
支持程度: 40%
框架: Spring Boot
測試框架: JUnit5, Mockito
性能測試: JMeter, Gatling
CI/CD: 需要重新設計 ⚠️

需要調整:
  - 完整重寫測試配置 (4 小時) ⚠️
  - 自訂 CI/CD (2 小時) ⚠️
```

### Go (🔴 不支持)

```yaml
支持程度: 10%
原因: 測試框架差異大

建議: 僅復用測試架構設計理念
```

---

## 📋 部署檢查清單

### 部署前

- [ ] 閱讀 `_bmad/_templates/README.md`
- [ ] 選擇部署方案 (A 或 B)
- [ ] 準備專案基本資訊 (name, type, description)

### 配置階段

- [ ] 創建 `.sentinel-config.yaml`
- [ ] 填寫 `project` 區塊
- [ ] 配置 `tech_stack` (語言、框架、版本)
- [ ] 標記 `priority_modules` (至少 3 個 Critical 模組)
- [ ] 調整 `test_directories` (如果結構不同)

### 測試階段

- [ ] 執行 "啟動 Sentinel Agent"
- [ ] 檢查生成的測試計畫
- [ ] 運行第一批測試
- [ ] 檢查覆蓋率報告

### 整合階段

- [ ] 自訂 Locust 性能測試 (API 端點)
- [ ] 設定 `ci_cd.enabled: true`
- [ ] 檢查生成的 CI workflow
- [ ] 本地測試 CI pipeline
- [ ] Push 到 GitHub,觀察 Actions

---

## 💡 最佳實踐建議

### 1. 模組化部署

```yaml
階段 1 (第 1 週):
  - 僅配置單元測試
  - 目標: 覆蓋率 30% → 50%

階段 2 (第 2 週):
  - 添加整合測試
  - 目標: 覆蓋率 50% → 70%

階段 3 (第 3 週):
  - 添加 E2E 測試
  - 添加性能測試

階段 4 (第 4 週):
  - 整合 CI/CD
  - 自動化所有流程
```

### 2. 團隊協作

```yaml
角色分工:
  Tech Lead:
    - 標記 priority_modules
    - 設定 coverage_targets
  
  QA Engineer:
    - 自訂 E2E 測試場景
    - 設定性能基準
  
  Backend Dev:
    - 編寫單元測試
    - 整合測試
  
  DevOps:
    - CI/CD 整合
    - 環境配置
```

### 3. 文檔維護

```yaml
必須更新:
  - README.md (添加測試說明)
  - CONTRIBUTING.md (測試規範)
  - .sentinel-config.yaml (priority_modules)

定期維護:
  - memories.md (Sentinel 學習內容)
  - change-tracker.yaml (變更記錄)
```

---

## 🔗 相關資源

- [模板使用指南](_bmad/_templates/README.md)
- [配置模板](sentinel-config.template.yaml)
- [Locust 模板](locustfile.template.py)
- [性能測試工作流](../_memory/sentinel-sidecar/workflows/performance-testing.md)
- [CI 自動化工作流](../_memory/sentinel-sidecar/workflows/ci-automation.md)

---

**結論:**

Sentinel Agent **可以部署到其他專案**,但需要 **15-120 分鐘的適配時間**,具體取決於:

1. ✅ 專案類型相似度 (Python → Python: 15 分鐘)
2. ⚠️ 技術棧差異 (Python → Node.js: 2 小時)
3. ⚠️ 業務邏輯複雜度 (簡單 CRUD: 30 分鐘, 複雜金融: 4 小時)

**推薦做法:** 使用模板化方案,建立組織內部的 Sentinel 模板庫。
