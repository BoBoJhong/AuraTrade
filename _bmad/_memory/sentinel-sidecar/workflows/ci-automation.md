# CI 自動化工作流 (CI Automation Workflow)

**目標:** GitHub Actions 自動化測試、品質檢查、安全掃描

---

## 工作流概覽

### CI Pipeline 結構

```
Push/PR → GitHub Actions 觸發
  │
  ├── Job 1: Backend Unit Tests (Python 3.11, 3.12)
  │       ├─ 安裝依賴
  │       ├─ 執行測試
  │       ├─ 產出覆蓋率
  │       └─ 上傳報告
  │
  ├── Job 2: Backend Integration Tests
  │       ├─ 啟動 PostgreSQL + Redis
  │       ├─ 執行 Migration
  │       └─ 執行測試
  │
  ├── Job 3: Frontend Tests
  │       ├─ 安裝 Node.js
  │       └─ 執行 Vitest
  │
  ├── Job 4: E2E Tests (Playwright)
  │       ├─ Docker Compose 啟動服務
  │       ├─ 執行場景測試
  │       └─ 上傳截圖
  │
  ├── Job 5: Performance Tests (Locust)
  │       ├─ 啟動後端
  │       ├─ 執行負載測試
  │       └─ PR 評論結果
  │
  ├── Job 6: Code Quality
  │       ├─ Black 格式檢查
  │       ├─ Flake8 Linting
  │       ├─ Bandit 安全掃描
  │       └─ Prettier (Frontend)
  │
  ├── Job 7: Security Scan
  │       ├─ Snyk 漏洞掃描
  │       └─ Trivy 容器掃描
  │
  └── Job 8: Test Summary
          └─ 彙總所有結果
```

---

## 觸發時機

### 1. Push 事件

```yaml
觸發分支:
  - main (主分支)
  - develop (開發分支)

動作:
  - 執行完整質量檢測
  - 防止破壞性變更合入
  - 維護主分支穩定性
```

### 2. Pull Request 事件

```yaml
觸發條件:
  - 建立 PR
  - 推送新 commit 到 PR
  - PR 重新開啟

動作:
  - 執行所有測試
  - 在 PR 中評論結果
  - 視覺化覆蓋率變化
  - 檢查性能回歸

品質閘門:
  - 單元測試通過率 ≥ 98%
  - 覆蓋率 ≥ 70%
  - 沒有 Critical 安全漏洞
  - 沒有格式錯誤
```

### 3. 手動觸發

```yaml
workflow_dispatch:
  使用場景:
    - 重新執行失敗的測試
    - 測試特定環境
    - 性能基準更新
```

---

## Job 詳細說明

### Job 1: Backend Unit Tests

```yaml
目的:
  驗證後端業務邏輯正確性

執行環境:
  - Python 3.11
  - Python 3.12 (矩陣測試)

測試範圍:
  - tests/unit/services/
  - tests/unit/core/
  - tests/unit/repositories/

成功標準:
  - 通過率 ≥ 98%
  - 覆蓋率 ≥ 70%
  - 無 Critical 故障

輸出:
  - JUnit XML 報告
  - Coverage XML (上傳 Codecov)
  - HTML 覆蓋率報告
```

### Job 2: Backend Integration Tests

```yaml
目的:
  驗證 API 端點與資料庫整合

服務依賴:
  - PostgreSQL 15 (健康檢查)
  - Redis 7 (快取)

測試流程:
  1. 啟動服務
  2. 執行 Migration
  3. 運行測試
  4. 清理資料

成功標準:
  - 所有 API 測試通過
  - 資料庫連線穩定
```

### Job 3: Frontend Tests

```yaml
目的:
  驗證前端元件與邏輯

測試框架:
  - Vitest (Unit Tests)
  - React Testing Library

成功標準:
  - 通過率 100%
  - 覆蓋率 ≥ 80%
```

### Job 4: E2E Tests

```yaml
目的:
  驗證完整用戶流程

工具:
  - Playwright (Chromium)

測試場景:
  - 用戶註冊登入
  - 股票查詢與分析
  - 投資組合管理
  - 價格警報設定

輸出:
  - HTML 報告
  - 截圖 (失敗案例)
  - 錄影 (失敗案例)
```

### Job 5: Performance Tests

```yaml
目的:
  驗證 API 性能不回歸

執行條件:
  - 僅在 Pull Request 時執行
  - 手動觸發

測試參數:
  - 50 併發用戶
  - 5 user/sec 增長
  - 2 分鐘持續時間

性能閾值:
  - P95 < 500ms
  - 失敗率 < 1%
  - RPS > 50

PR 評論:
  自動發布性能結果至 PR
```

### Job 6: Code Quality

```yaml
目的:
  維護代碼品質與一致性

Backend 檢查:
  - Black: 代碼格式化
  - Flake8: Linting
  - Mypy: 類型檢查
  - Pylint: 進階 Linting
  - Bandit: 安全掃描

Frontend 檢查:
  - Prettier: 格式化
  - ESLint: Linting
  - TypeScript: 類型檢查

失敗條件:
  - 格式錯誤
  - Linting 錯誤 > 0
  - 安全問題 (severity: high)
```

### Job 7: Security Scan

```yaml
目的:
  檢測安全漏洞與依賴問題

工具:
  - Snyk: 依賴漏洞掃描
  - Trivy: 容器掃描
  - Bandit: Python 代碼安全

檢查項目:
  - OWASP Top 10
  - 已知 CVE 漏洞
  - 依賴套件版本
  - 敏感資訊洩露

警告條件:
  - Critical: 阻止 merge
  - High: 警告但不阻止
  - Medium/Low: 僅記錄
```

### Job 8: Test Summary

```yaml
目的:
  彙總所有測試結果

產出內容:
  - 測試通過/失敗統計
  - 覆蓋率變化
  - 性能變化
  - 安全問題清單

動作:
  - 生成 GitHub Summary
  - 更新 PR Status
  - 通知開發者 (失敗時)
```

---

## 品質閘門 (Quality Gates)

### 必須條件 (Blocking)

```yaml
阻止 Merge 的條件:
  - 單元測試通過率 < 98%
  - 覆蓋率 < 70%
  - Critical 安全漏洞 > 0
  - 格式檢查失敗
  - E2E 關鍵場景失敗
```

### 警告條件 (Warning)

```yaml
不阻止但需評估:
  - 性能下降 > 10%
  - High 安全漏洞 > 0
  - 覆蓋率下降 > 5%
  - Linting 警告 > 10
```

---

## 每日定時任務

### Nightly Build

```yaml
schedule:
  - cron: '0 2 * * *'  # 每天凌晨 2 點 (UTC)

任務:
  - 完整測試套件
  - 長時間性能測試 (10 分鐘)
  - 安全全面掃描
  - 依賴更新檢查
  - 資料庫備份測試

報告:
  - 發送日報郵件
  - 更新 Dashboard
  - 記錄性能趨勢
```

---

## 通知機制

### GitHub 通知

```yaml
成功時:
  - ✅ PR Status Check 顯示綠色
  - 成功的測試統計評論

失敗時:
  - ❌ PR Status Check 顯示紅色
  - 詳細錯誤訊息評論
  - 連結失敗的 workflow run
  - 標記 PR 需要修復
```

### Slack 通知 (可選)

```yaml
通知內容:
  - 測試結果摘要
  - 失敗的 Job 清單
  - 聯繫開發者
  - 連結到 GitHub Actions

觸發時機:
  - main/develop 分支失敗
  - 夜間建構失敗
  - Critical 安全問題
```

---

## 優化建議

### 1. 增量測試

```yaml
目的:
  僅測試變更的模組

實現:
  - 使用 pytest --testmon
  - git diff 分析
  - 依賴圖追蹤

效果:
  - 測試時間縮短 60-80%
  - 快速回饋循環
```

### 2. 快取優化

```yaml
快取策略:
  - pip cache (依賴套件)
  - npm cache (Node 模組)
  - Docker layer cache
  - pytest cache

效果:
  - 建構時間減少 50%+
```

### 3. 並行執行

```yaml
並行策略:
  - 多 Job 並行
  - pytest-xdist (多進程)
  - Matrix Strategy (多版本)

效果:
  - 總運行時間減少 70%+
```

---

## 最佳實踐

```yaml
1. 保持測試快速:
   - 單元測試 < 5 分鐘
   - 整合測試 < 10 分鐘
   - E2E < 15 分鐘

2. Fail Fast:
   - 啟用 --exitfirst
   - 優先執行易失敗的測試

3. 清楚的錯誤訊息:
   - 詳細的 traceback
   - 截圖與日誌
   - 重現步驟

4. 定期維護:
   - 每週更新依賴
   - 清理過時的快取
   - 審查失敗的測試

5. 文件化:
   - 測試目的
   - CI 配置說明
   - 排雜記錄
```
