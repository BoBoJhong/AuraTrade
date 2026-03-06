# Sentinel Agent 快速啟動 - AuraTrade

**更新日期**: 2026-02-11  
**適用專案**: AuraTrade AI 投資分析系統

---

## 🚀 一鍵設置 (首次使用)

### Windows PowerShell

```powershell
# 確保在專案根目錄 C:\Users\coolc\AuraTrade

# 步驟 1: 安裝前端測試框架
.\scripts\setup-frontend-testing.ps1

# 步驟 2: 驗證配置檔
cat .sentinel-config.yaml

# 步驟 3: (可選) 執行 Sentinel 初始化
*init
```

### 預期輸出

```
✅ Vitest 已安裝
✅ vitest.config.ts 已創建
✅ tests/setup.ts 已創建
✅ package.json 測試腳本已更新

📋 可用命令：
  npm run test              # 執行測試
  npm run test:ui           # 測試 UI 介面
  npm run test:coverage     # 覆蓋率報告
```

---

## 📋 常用命令速查

### 測試生成

#### 後端 (Python)

```bash
# 針對高風險 AI 服務
*generate-tests --file=backend/apps/services/gemini_service.py

# 針對股價服務
*generate-tests --file=backend/apps/services/yahoo_finance.py

# 針對整個 services 目錄
*generate-tests --module=backend/apps/services/
```

#### 前端 (TypeScript/React)

```bash
# 針對股票圖表元件
*generate-tests --file=frontend/src/components/stocks/StockChart.tsx

# 針對 WebSocket Hook
*generate-tests --file=frontend/src/hooks/useStockWebSocket.ts

# 針對整個 stocks 元件
*generate-tests --module=frontend/src/components/stocks/
```

---

### 測試執行

#### 完整測試

```bash
# Sentinel 完整週期 (自動)
*full-cycle

# 手動執行所有測試
npm run test:all      # 根目錄統一腳本
```

#### 後端測試

```bash
cd backend

# 單元測試
pytest tests/unit -v

# 整合測試
pytest tests/integration -v

# 性能測試
pytest tests/performance -v -m performance

# 覆蓋率報告
pytest --cov=apps --cov-report=html
```

#### 前端測試

```bash
cd frontend

# 單元測試
npm run test

# 監聽模式
npm run test:watch

# UI 模式
npm run test:ui

# 覆蓋率
npm run test:coverage
```

#### 負載測試 (Locust)

```bash
# 本機負載測試
locust -f tests/performance/load_test.py --headless \
  --users 100 --spawn-rate 10 --run-time 1m \
  --host http://localhost:8000
```

---

### 品質檢查

```bash
# 風險地圖 (識別高複雜度區域)
*risk-map

# 品質報告 (整體覆蓋率與趨勢)
*quality-report

# CI 準備檢查
*ci-check
```

---

## 🎯 建議工作流

### 工作流 1: 開發新功能 (TDD)

```bash
# 1. 使用 Sentinel 生成測試框架
*tdd-mode
需求: 實現股票價格提醒功能
路徑: backend/apps/services/price_alert_service.py

# 2. Sentinel 自動生成測試案例與空函數

# 3. 填寫實現代碼

# 4. 執行測試驗證
pytest tests/unit/services/test_price_alert_service.py -v

# 5. 所有測試通過 → 提交代碼
```

---

### 工作流 2: 每週品質檢查

```bash
# 1. 重新掃描專案
*scan-project

# 2. 識別新增風險
*risk-map

# 3. 產出品質報告
*quality-report

# 4. 查看報告
cat tests/reports/quality-reports/QR-*.md

# 5. 針對高風險區域補強測試
*generate-tests --file=<high-risk-file>
```

---

### 工作流 3: PR 前檢查

```bash
# 1. 執行完整測試
pytest tests/                  # 後端
npm run test                   # 前端

# 2. 檢查覆蓋率
pytest --cov=apps --cov-report=term
npm run test:coverage

# 3. 執行 Linting
flake8 backend/apps/           # 後端
npm run lint                   # 前端

# 4. Sentinel 品質報告
*quality-report

# 5. 推送 (GitHub Actions 自動執行 CI)
git push origin feature-branch
```

---

## 📂 重要路徑參考

### 配置檔

- `.sentinel-config.yaml` - Sentinel 主配置
- `frontend/vitest.config.ts` - Vitest 配置
- `backend/pytest.ini` - Pytest 配置

### 測試目錄

- `tests/unit/` - 單元測試 (✅ 已存在)
- `tests/integration/` - 整合測試 (✅ 已存在)
- `tests/e2e/` - E2E 測試 (🆕 待創建)
- `tests/performance/` - 性能測試 (🆕 待創建)

### 報告目錄

- `tests/reports/test-plans/` - 測試計畫
- `tests/reports/test-reports/` - 測試報告
- `tests/reports/risk-maps/` - 風險地圖
- `tests/reports/quality-reports/` - 品質報告

### Sentinel 記憶

- `_bmad/_memory/sentinel-sidecar/` - Sentinel 持久化記憶

---

## 🔧 常見問題

### Q: Vitest 安裝失敗怎麼辦？

```powershell
# 手動安裝
cd frontend
npm install -D vitest @vitest/ui @testing-library/react @testing-library/jest-dom happy-dom
```

### Q: 如何查看 Sentinel 識別的高風險區域？

```bash
*risk-map

# 或查看報告
cat tests/reports/risk-maps/RM-*.md
```

### Q: 前後端測試如何統一執行？

```bash
# 建議在根目錄 package.json 添加
{
  "scripts": {
    "test:all": "npm run test:backend && npm run test:frontend",
    "test:backend": "cd backend && pytest tests/",
    "test:frontend": "cd frontend && npm run test"
  }
}
```

### Q: CI 測試失敗怎麼辦？

1. 查看 GitHub Actions 日誌
2. 本機重現: `pytest tests/ -v`
3. 使用 Sentinel 修復建議: `*fix-proposal`

---

## 📞 獲取幫助

- **Sentinel 文檔**: `_bmad/_memory/sentinel-sidecar/README.md`
- **完整工作流**: `_bmad/_memory/sentinel-sidecar/workflows/`
- **測試最佳實踐**: `_bmad/_memory/sentinel-sidecar/knowledge/best-practices.md`

---

**版本**: 1.0.0  
**維護者**: AuraTrade Development Team  
**最後更新**: 2026-02-11
