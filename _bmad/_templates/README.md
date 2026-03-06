# Sentinel Agent 通用化模板

##  目錄結構

```
_bmad/_templates/
 README.md                           # 本文件
 sentinel-config.template.yaml      #  配置模板
 locustfile.template.py             #  性能測試模板
 init-sentinel.ps1                  #  初始化腳本 (PowerShell)
 init-sentinel.sh                   # TODO: 初始化腳本 (Bash)
 conftest.template.py               # TODO: Pytest 配置模板
 ci-workflow.template.yml           # TODO: CI/CD 模板
```

---

##  快速開始

### 方法 1: 使用初始化腳本 (推薦)

```powershell
# PowerShell
.\_bmad\_templates\init-sentinel.ps1 -ProjectName "MyProject" -ProjectType "fullstack"

# Bash (TODO)
bash _bmad/_templates/init-sentinel.sh --project-name "MyProject" --project-type "fullstack"
```

### 方法 2: 手動配置

1. **複製配置模板**
   ```bash
   cp _bmad/_templates/sentinel-config.template.yaml .sentinel-config.yaml
   ```

2. **編輯配置文件**
   - 替換 {{PROJECT_NAME}}  你的專案名稱
   - 替換 {{PROJECT_TYPE}}  python|nodejs|fullstack|java|go
   - 替換 {{PROJECT_ROOT}}  專案根目錄絕對路徑
   - 填寫 priority_modules (關鍵模組)

3. **創建測試目錄**
   ```bash
   mkdir -p tests/{unit,integration,e2e,performance,reports}
   mkdir -p _bmad/_memory/sentinel-sidecar/workflows
   ```

4. **複製性能測試模板** (可選)
   ```bash
   cp _bmad/_templates/locustfile.template.py tests/performance/locustfile.py
   ```

5. **啟動 Sentinel**
   ```bash
   # 在 Copilot Chat 中執行
   "啟動 Sentinel Agent"
   ```

---

##  配置說明

### 必填項目

```yaml
project:
  name: "ProjectName"        # 專案名稱
  type: "fullstack"          # python|nodejs|fullstack|java|go
  root: "/path/to/project"   # 絕對路徑
  description: "描述"
```

### 技術棧配置

根據專案類型調整:

```yaml
# Python 專案
tech_stack:
  backend:
    language: "Python"
    version: "3.11"
    framework: "FastAPI"
    test_framework: "Pytest"

# Node.js 專案
tech_stack:
  frontend:
    language: "TypeScript"
    framework: "React"
    build_tool: "Vite"
    test_framework: "Jest"
```

### 優先模組標記 (重要!)

標記專案的關鍵模組,Sentinel 會優先測試:

```yaml
priority_modules:
  critical:  # 最高優先級 (安全、支付、核心業務)
    - name: "AuthModule"
      path: "src/auth"
      reason: "認證安全核心"
      target_coverage: 95
  
  high:      # 高優先級 (重要功能)
    - name: "OrderModule"
      path: "src/orders"
      reason: "訂單處理"
      target_coverage: 85
  
  medium:    # 中優先級 (一般功能)
    - name: "NotificationModule"
      path: "src/notifications"
      target_coverage: 70
```

---

##  專案類型適配指南

### Python 專案

```yaml
tech_stack:
  backend:
    language: "Python"
    framework: "FastAPI|Django|Flask"
    test_framework: "Pytest"

test_directories:
  unit: "tests/unit"
  integration: "tests/integration"
```

**依賴安裝:**
```bash
pip install pytest pytest-asyncio pytest-cov locust
```

### Node.js 專案

```yaml
tech_stack:
  frontend:
    language: "JavaScript|TypeScript"
    framework: "React|Vue|Express"
    test_framework: "Jest|Vitest"

test_directories:
  unit: "tests/unit"
  e2e: "tests/e2e"
```

**依賴安裝:**
```bash
npm install --save-dev jest @testing-library/react playwright
```

### Fullstack 專案

同時配置 backend 和 frontend 區塊。

### Java 專案 (實驗性)

```yaml
tech_stack:
  backend:
    language: "Java"
    framework: "Spring Boot"
    test_framework: "JUnit5"
```

### Go 專案 (實驗性)

```yaml
tech_stack:
  backend:
    language: "Go"
    framework: "Gin|Echo"
    test_framework: "testing"
```

---

##  可移植性清單

###  可直接復用 (無需修改)

- [ ] 測試架構設計 (test pyramid, coverage targets)
- [ ] 測試執行配置 (parallel, timeout, retry)
- [ ] 風險識別邏輯 (complexity, coverage thresholds)
- [ ] 排除規則 (node_modules, __pycache__, etc.)
- [ ] 工作流框架 (performance-testing.md, ci-automation.md)

###  需要調整 (專案特定)

- [ ] project 區塊 (name, type, root, description)
- [ ] 	ech_stack 區塊 (language, framework, versions)
- [ ] priority_modules 區塊 (專案的關鍵模組)
- [ ] 	est_directories 路徑 (如果專案結構不同)
- [ ] ci_cd.enabled (設為 true 自動生成 workflow)

###  需要自訂 (業務邏輯)

- [ ] Locust 性能測試 (API endpoints, test data)
- [ ] E2E 測試場景 (用戶流程)
- [ ] CI/CD workflow (如果專案有特殊需求)

---

##  使用建議

### 新專案

1. 使用 init-sentinel.ps1 自動初始化
2. 填寫 priority_modules
3. 執行 "啟動 Sentinel Agent"
4. Sentinel 會自動生成測試計畫和測試代碼

### 現有專案

1. 手動創建 .sentinel-config.yaml
2. 設定 preserve_existing: true (保留現有測試)
3. 標記 priority_modules
4. Sentinel 會補充缺失的測試

### 多專案共用

1. Fork AuraTrade 專案的 _bmad/_templates/ 目錄
2. 放入你的組織私有 repo
3. 團隊成員從模板初始化新專案

---

##  進階功能

### 自動生成 CI/CD

設定 ci_cd.enabled: true 後,Sentinel 會自動生成:

- .github/workflows/tests.yml (GitHub Actions)
- 或 .gitlab-ci.yml (GitLab CI)
- 或 Jenkinsfile (Jenkins)

### 性能基準測試

```bash
# 執行性能測試並建立基準
locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
       --users 100 --spawn-rate 10 --run-time 2m --headless

# 基準數據存儲在
tests/reports/performance/baseline.json
```

### 測試覆蓋率追蹤

Sentinel 會自動記錄覆蓋率變化:

```yaml
# _bmad/_memory/sentinel-sidecar/memories.md
history:
  - date: "2026-02-11"
    coverage: 35%
  - date: "2026-02-12"
    coverage: 55%  # +20%
```

---

##  貢獻

歡迎貢獻更多語言/框架的模板!

請提交 PR 包含:
- [ ] 配置模板 (sentinel-config.{lang}.template.yaml)
- [ ] 測試框架示例
- [ ] CI/CD workflow 模板
- [ ] 文檔說明

---

##  相關資源

- [Sentinel Agent 使用指南](../README.md)
- [性能測試工作流](../../_memory/sentinel-sidecar/workflows/performance-testing.md)
- [CI 自動化工作流](../../_memory/sentinel-sidecar/workflows/ci-automation.md)
- [AuraTrade 完整範例](../../..)

---

**版本:** 1.0.0  
**更新:** 2026-02-11  
**維護:** Sentinel Agent Team
