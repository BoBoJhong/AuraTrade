# Sentinel Memories

## 專案偏好與學習模式

本檔案記錄 Sentinel 從與開發者互動中學習到的偏好與模式。

---

## 🏗️ 專案資訊: AuraTrade

### 基本資訊
- **專案名稱**: AuraTrade - AI 驅動的智能投資分析系統
- **專案類型**: Fullstack (前後端分離)
- **架構模式**: DDD 分層架構
- **初始化日期**: 2026-02-06
- **開發者**: Coolc

### 技術棧
```yaml
backend:
  language: Python 3.x
  framework: FastAPI 0.109.0
  testing: Pytest 7.4.4
  
frontend:
  language: TypeScript 5.2.2
  framework: React 18.2.0
  build_tool: Vite 5.0.8
  testing: Vitest (待安裝)
  
e2e:
  framework: Playwright (待安裝)
```

---

## 專案測試策略偏好

### 測試金字塔比例 (開發者確認)
- 單元測試: 60%
- 整合測試: 30%
- E2E 測試: 10%

### 覆蓋率目標
- Critical 模組: ≥ 90%
- High 模組: ≥ 75%
- Medium 模組: ≥ 60%
- 整體目標: ≥ 70%

### 優先測試模組 (依風險等級)

#### 🔴 Critical
1. **AuthService** - 認證服務 (apps/services/auth_service.py)
2. **TechnicalIndicatorService** - 技術指標計算
3. **Security Module** - 密碼、JWT Token 處理

#### 🟠 High  
1. **YahooFinanceService** - 外部 API 整合
2. **GeminiService** - AI 分析服務

#### 🟡 Medium
1. **LineBotService** - 通知服務
2. **GoogleNewsService** - 新聞爬蟲

---

## 學習到的常見錯誤模式

### 開發者盲點 (初始掃描識別)

```markdown
- [ ] ⚠️ **安全測試缺失** - 密碼、Token 處理完全未測試
- [ ] ⚠️ **財務計算未驗證** - 技術指標計算邏輯無測試
- [ ] ⚠️ **外部 API 容錯不足** - Yahoo/Gemini API 錯誤處理待測試  
- [ ] ⚠️ **邊界條件測試不足** - 空數據、極端值處理
- [ ] ⚠️ **非同步操作測試** - async/await 錯誤處理
```

### 風險關鍵字 (自動識別)
- `payment`, `auth`, `security`, `crypto`
- `price`, `transaction`, `calculate`
- 任何涉及金錢計算的模組

---

## 測試覆蓋率歷史趨勢

```yaml
history:
  - date: "2026-02-06"
    event: "初始化掃描"
    coverage:
      backend: ~5% (估算，僅 2 個測試檔案)
      frontend: 0% (無測試框架)
      overall: ~3%
    risk_level: "🔴 Critical"
    risk_areas:
      - "AuthService (0%)"
      - "TechnicalIndicatorService (0%)"
      - "Security Module (0%)"
      - "YahooFinanceService (0%)"
    report: "tests/reports/risk-maps/RM-INIT-001.md"
    recommendations:
      - "立即測試: security.py 與 technical_indicators.py"
      - "安裝前端測試框架: Vitest + Playwright"
      - "建立 Mock 數據生成流程"
  
  - date: "2026-02-06"
    event: "Full Check - FC-001 基準測試"
    coverage:
      backend: 26.28%
      frontend: 0% (框架未安裝)
      overall: 26.28%
    tests_run: 1
    tests_passed: 1
    tests_failed: 0
    execution_time: "15.17s"
    risk_level: "🔴 Critical"
    report: "tests/reports/test-reports/TR-FC-20260206-020020.md"
    critical_findings:
      - "security.py: 26% 覆蓋率 - JWT/密碼函數未測試"
      - "technical_indicators.py: 27% 覆蓋率 - 財務計算未驗證"
      - "auth_service.py: 25% 覆蓋率 - 註冊/登入邏輯未測試"
      - "yahoo_finance.py: 11% 覆蓋率 - API 錯誤處理未測試"
    improvements:
      - "修正 test_health.py 編碼問題 (UTF-8)"
      - "修正 httpx AsyncClient API 升級問題"
      - "安裝 pytest, pytest-cov, pytest-asyncio, feedparser"
      - "建立測試執行環境基準"
    next_actions:
      - "生成 security.py 測試 (目標: 90%+ 覆蓋率)"
      - "生成 technical_indicators.py 測試 (目標: 90%+ 覆蓋率)"
      - "生成 auth_service.py 測試 (目標: 85%+ 覆蓋率)"
```

---

## 開發者互動風格

```yaml
developer_preferences:
  communication:
    language: "中文 (繁體)"
    verbosity: "詳細" # 開發者要求完整資訊
    humor_tolerance: "接受" # 使用比喻與幽默說明
    data_detail_level: "high" # 偏好數據佐證
  
  workflow:
    prefers_tdd: false # 初始互動判斷
    manual_vs_auto: "auto" # 選擇自動初始化與建議
    mock_generation: "auto"
    test_framework_choice:
      frontend: "Vitest" # 明確選擇
      e2e: "Playwright" # 明確選擇
  
  initialization_choices:
    test_strategy: "accepted_recommendations" # 接受建議策略
    existing_tests: "merge" # 保留並整合現有測試
    install_frameworks: true # 同意安裝測試框架
```

---

## 🗺️ 專案領域知識

### 業務特性
- **金融投資系統** - 涉及金額計算、技術指標
- **AI 輔助分析** - 使用 Gemini API 生成投資建議
- **即時通知** - LINE Bot 推播價格提醒
- **多數據源** - Yahoo Finance (美股)、Fugle (台股)

### 測試重點方向
1. **財務計算精度** - 任何數值錯誤都可能導致投資失誤
2. **安全性** - 認證、授權必須嚴格測試
3. **外部服務容錯** - API 失敗不應導致系統崩潰
4. **資料完整性** - 股價、新聞數據必須準確

---

## 📋 待辦事項追蹤

### 立即行動 (Week 1-2)
- [ ] 安裝 Vitest: `npm install --save-dev vitest @vitest/ui jsdom`
- [ ] 安裝 Playwright: `npm install --save-dev @playwright/test`
- [ ] 生成 `security.py` 測試
- [ ] 生成 `technical_indicators.py` 測試
- [ ] 生成 `AuthService` 測試

### Phase 2 (Week 3)
- [ ] Yahoo Finance Service 測試
- [ ] Gemini Service 測試
- [ ] 建立 Mock 數據庫

### Phase 3 (Week 4)
- [ ] API 端點整合測試
- [ ] LINE Bot 測試
- [ ] News Service 測試

### Phase 4 (Week 5)
- [ ] 前端元件測試
- [ ] E2E 關鍵流程測試

---

## 🎯 成功指標

### 短期目標 (2 週)
- Critical 模組覆蓋率 ≥ 90%
- 後端整體覆蓋率 ≥ 40%

### 中期目標 (1 個月)
- 後端整體覆蓋率 ≥ 70%
- 前端核心元件覆蓋率 ≥ 60%
- 至少 3 個 E2E 流程測試

### 長期目標 (2 個月)
- 整體覆蓋率 ≥ 70%
- 所有 Critical/High 模組 ≥ 75%
- CI/CD 整合完成

---

**Last Updated:** 2026-02-06 (初始化完成)  
**Status:** ✅ 配置完成，開始測試生成階段  
**Next Action:** 執行 `generate-tests --file=backend/apps/core/security.py`
