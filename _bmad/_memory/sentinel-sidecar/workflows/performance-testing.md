# 性能測試工作流 (Performance Testing Workflow)

**目標:** 使用 Locust 執行 API 負載測試與壓力測試

---

## 工作流觸發

**命令:** `*performance-test` 或 `*perf` 或 `*load-test`

**使用時機:**
- 新功能開發完成後,驗證性能
- Release 前的性能基準測試
- 優化後的效果驗證
- CI/CD 自動化流程

---

## 階段 1: 環境準備

### 1.1 安裝 Locust

```yaml
檢查安裝:
  命令: pip show locust
  若未安裝: pip install locust
  驗證: locust --version
```

### 1.2 啟動後端服務

```yaml
本地測試:
  命令: cd backend && uvicorn main:app --host 0.0.0.0 --port 8000
  或: docker-compose up backend
  檢查: curl http://localhost:8000/health

CI 環境:
  Docker Compose 自動啟動
  等待 10 秒確保服務就緒
```

### 1.3 準備測試用戶

```yaml
注意:
  - Locust 會自動註冊不存在的測試用戶
  - 或手動建立 50 個 loadtest 用戶
  - 測試數據位於 locustfile.py 中
```

---

## 階段 2: 執行性能測試

### 2.1 Web UI 模式 (本地開發)

```bash
# 啟動 Locust Web UI
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# 瀏覽器開啟: http://localhost:8089
# 設定參數:
#   - Number of users: 100 (同時線上用戶數)
#   - Spawn rate: 10 (每秒增加的用戶數)
#   - Host: http://localhost:8000
```

**Web UI 功能:**
- 即時性能圖表 (RPS, Response Time, Failures)
- 請求統計 (各 endpoint 性能)
- 用戶數動態調整
- 失敗案例追蹤

### 2.2 Headless 模式 (CI/CD)

```bash
# 基本壓測 (50 用戶, 2 分鐘)
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 2m \
  --headless

# 高負載測試 (200 用戶, 5 分鐘)
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users 200 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless \
  --html tests/reports/performance/load-test-report.html \
  --csv tests/reports/performance/load-test

# 壓力測試 (500 用戶 持續攻擊)
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users 500 \
  --spawn-rate 50 \
  --run-time 10m \
  --headless
```

### 2.3 指定特定場景

```bash
# 只測試認證流程
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users 100 \
  --headless \
  AuthLoadTest

# 只測試股票 API
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users 200 \
  --headless \
  StockAPILoadTest

# 混合場景 (默認)
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users 150 \
  --headless \
  MixedWorkload
```

---

## 階段 3: 結果分析

### 3.1 關鍵指標

```yaml
性能指標:
  RPS (Requests Per Second):
    目標: > 100 RPS
    優異: > 500 RPS
  
  平均響應時間:
    目標: < 200ms
    優異: < 100ms
  
  P95 響應時間:
    目標: < 500ms
    優異: < 300ms
  
  P99 響應時間:
    目標: < 1000ms
    優異: < 500ms
  
  失敗率:
    目標: < 1%
    優異: < 0.1%

API 端點性能:
  GET /api/v1/stocks/:symbol:
    目標: < 150ms
    優異: < 80ms
  
  POST /api/v1/auth/login:
    目標: < 300ms (包含 bcrypt 雜湊)
    優異: < 200ms
  
  GET /api/v1/stocks/:symbol/indicators:
    目標: < 500ms (複雜計算)
    優異: < 300ms
```

### 3.2 報告產出

```yaml
HTML 報告:
  路徑: tests/reports/performance/load-test-report.html
  內容:
    - 整體性能摘要
    - 各 endpoint 詳細統計
    - 響應時間分佈圖
    - 失敗請求清單

CSV 報告:
  - load-test_stats.csv (統計數據)
  - load-test_stats_history.csv (時間序列數據)
  - load-test_failures.csv (失敗記錄)

終端輸出:
  即時顯示:
    - 當前 RPS
    - 平均響應時間
    - 用戶數
    - 失敗數
```

### 3.3 性能警告

```yaml
自動檢測:
  失敗率 > 5%:
    級別: CRITICAL
    動作: 停止測試、通知開發者
  
  P95 > 1000ms:
    級別: WARNING
    動作: 記錄警告、繼續測試
  
  RPS < 50:
    級別: INFO
    動作: 檢查伺服器負載
```

---

## 階段 4: 性能優化建議

### 4.1 常見瓶頸

```yaml
資料庫查詢:
  問題: N+1 查詢
  解決: 使用 joinedload() eager loading
  效果: 響應時間減少 50-80%

外部 API:
  問題: 同步等待
  解決: async/await + asyncio.gather()
  效果: 並發執行,速度提升 3-5x

快取:
  問題: 重複計算
  解決: Redis 快取 + TTL
  效果: 響應時間減少 90%+

序列化:
  問題: JSON 序列化慢
  解決: 使用 orjson 或 ujson
  效果: 速度提升 2-3x
```

### 4.2 性能優化檢測清單

```yaml
☐ 添加資料庫索引 (WHERE/JOIN 字段)
☐ 啟用 Redis 快取 (熱點數據)
☐ 使用 Connection Pooling
☐ 優化 SQL 查詢 (EXPLAIN ANALYZE)
☐ 實施 API Rate Limiting
☐ 啟用 GZIP 壓縮
☐ 靜態資源 CDN 加速
☐ 實施分頁 (Pagination)
☐ 異步處理長時任務 (Celery/RQ)
☐ 水平擴展 (Load Balancer)
```

---

## 階段 5: CI 整合

### 5.1 GitHub Actions 觸發

```yaml
觸發時機:
  - Pull Request (每次 PR 自動執行)
  - 手動觸發 (workflow_dispatch)
  - 定時測試 (每天凌晨 2 點)

測試參數:
  Users: 50 (輕量級)
  Spawn Rate: 5
  Duration: 2 分鐘
  目的: 快速回饋,不阻塞開發

PR 評論:
  自動發布性能測試結果
  包含: RPS, 響應時間, 失敗率
  連結完整報告
```

### 5.2 性能基準 (Baseline)

```yaml
基準記錄:
  儲存位置: tests/reports/performance/baseline.json
  更新時機: 重大修改後
  內容:
    - 各 endpoint 的基準響應時間
    - RPS 基準
    - 失敗率基準

回歸檢測:
  若性能下降 > 20%:
    動作: CI 失敗、阻止 merge
    通知: 開發者調查
  
  若性能提升 > 20%:
    動作: 更新基準
    通知: 表彰優化
```

---

## 階段 6: 持續監控

### 6.1 生產環境監控

```yaml
APM 工具:
  - New Relic
  - Datadog
  - Prometheus + Grafana

監控指標:
  - API 響應時間
  - 資料庫查詢時間
  - CPU/Memory 使用率
  - 錯誤率
  - 併發用戶數
```

### 6.2 報警設定

```yaml
警告閾值:
  P95 > 500ms: 警告
  P99 > 1000ms: 緊急
  錯誤率 > 1%: 致命
  RPS 異常曲線: 警告
```

---

## 輸出文件

```yaml
測試報告:
  - tests/reports/performance/PERF-{date}-{seq}.md
  - tests/reports/performance/load-test-report.html
  - tests/reports/performance/load-test_stats.csv

基準記錄:
  - tests/reports/performance/baseline.json

警告記錄:
  - tests/reports/performance/alerts.log
```

---

## 範例命令

```bash
# 1. 快速測試 (2 分鐘)
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users 50 --spawn-rate 5 --run-time 2m --headless

# 2. 完整測試並產出報告
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users 100 --spawn-rate 10 --run-time 5m \
  --headless \
  --html tests/reports/performance/load-test-report.html \
  --csv tests/reports/performance/load-test

# 3. 壓力測試
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users 500 --spawn-rate 50 --run-time 10m --headless

# 4. 指定場景測試
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users 100 --headless \
  StockAPILoadTest
```
