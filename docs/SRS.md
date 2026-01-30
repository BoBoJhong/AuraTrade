# AuraTrade 軟體需求規格書 (SRS)

## 文檔版本控制

| 版本 | 日期 | 作者 | 變更描述 |
|------|------|------|----------|
| 1.1 | 2026-01-30 | Development Team | 更新實作狀態：完成 Phase 1 核心功能 |
| 1.0 | 2026-01-29 | Development Team | 初始版本 - 基於 PRD v1.0 |

---

## 1. Introduction (簡介)

### 1.1 Purpose (目的)

本軟體需求規格書 (SRS) 定義 AuraTrade 系統的完整技術需求。本文檔旨在：

- 將 PRD 中的產品需求轉換為詳細的技術規格
- 為開發團隊提供清晰的實作指南
- 為測試團隊提供驗證基準
- 確保需求完整且可追溯

**目標讀者**：

- 開發團隊（前端、後端、全端工程師）
- QA 測試團隊
- 系統架構師
- 專案經理

### 1.2 Scope (範圍)

**系統名稱**: AuraTrade - AI 驅動的智能投資分析系統

**系統目標**:

- 為新手投資者提供即時股價監控與 AI 投資建議
- 整合多維度數據源（股價、新聞、社群情緒）
- 透過 LINE 提供即時通知服務
- 生成定期投資報表

**系統邊界**:

- **包含**: Web 應用（React）、後端 API（FastAPI）、資料庫（PostgreSQL）、爬蟲系統、AI 分析引擎
- **不包含**: 原生行動應用（Phase 4 擴展）、自動下單功能（Phase 4 擴展）

### 1.3 Definitions, Acronyms, and Abbreviations (定義、縮寫與簡稱)

| 術語 | 全稱 | 說明 |
|------|------|------|
| **AC** | Acceptance Criteria | 驗收標準 |
| **AI** | Artificial Intelligence | 人工智能 |  
| **API** | Application Programming Interface | 應用程式介面 |
| **BR** | Business Rule | 業務規則 |
| **DAU** | Daily Active Users | 日活躍用戶 |
| **DDD** | Domain-Driven Design | 領域驅動設計 |
| **E2E** | End-to-End | 端對端測試 |
| **ER** | Entity-Relationship | 實體關係圖 |
| **FR** | Functional Requirement | 功能需求 |
| **JWT** | JSON Web Token | JSON 網頁令牌 |
| **KPI** | Key Performance Indicator | 關鍵績效指標 |
| **MVP** | Minimum Viable Product | 最小可行產品 |
| **NFR** | Non-Functional Requirement | 非功能需求 |
| **ORM** | Object-Relational Mapping | 物件關聯對映 |
| **PRD** | Product Requirements Document | 產品需求文檔 |
| **RBAC** | Role-Based Access Control | 基於角色的存取控制 |
| **REQ** | Requirement | 技術需求 |
| **REST** | Representational State Transfer | 表述性狀態轉移 |
| **RTM** | Requirements Traceability Matrix | 需求追溯矩陣 |
| **SDD** | Software Design Document | 軟體設計文檔 |
| **SRS** | Software Requirements Specification | 軟體需求規格書 |
| **TDD** | Test-Driven Development | 測試驅動開發 |
| **US** | User Story | 用戶故事 |
| **UUID** | Universally Unique Identifier | 通用唯一識別碼 |
| **WAU** | Weekly Active Users | 週活躍用戶 |

### 1.4 References (參考文獻)

- **PRD**: `docs/PRD.md` - AuraTrade 產品需求文檔 v1.0
- **IEEE 830-1998**: IEEE Recommended Practice for Software Requirements Specifications
- **ISO/IEC/IEEE 29148:2018**: Systems and software engineering — Life cycle processes — Requirements engineering
- **FastAPI Documentation**: <https://fastapi.tiangolo.com/>
- **React Documentation**: <https://react.dev/>
- **PostgreSQL Documentation**: <https://www.postgresql.org/docs/>

### 1.5 Overview (文檔概述)

本 SRS 文檔結構如下：

- **Section 2**: 系統整體描述（系統視角、功能總覽、用戶類別、運行環境、約束條件）
- **Section 3**:详細需求（外部介面、功能需求、非功能需求、資料庫需求、設計約束）
- **Section 4**: 需求追溯矩陣 (RTM)

---

## 2. Overall Description (整體描述)

### 2.1 Product Perspective (產品視角)

AuraTrade 是一個**獨立的全新系統**，不是既有系統的延伸或升級。

**系統上下文圖**:

```
                          ┌─────────────┐
                          │   用戶      │
                          └──────┬──────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
              ┌─────▼────┐ ┌────▼─────┐ ┌───▼────┐
              │ Web App  │ │LINE Bot  │ │Browser │
              └─────┬────┘ └────┬─────┘ └───┬────┘
                    └────────────┼───────────┘
                                 │
                         ┌───────▼────────┐
                         │  AuraTrade     │
                         │  Backend API   │
                         └───┬────────┬───┘
                             │        │
                 ┌───────────┼────────┼──────────────┐
                 │           │        │              │
          ┌──────▼─────┐ ┌──▼────┐ ┌▼──────┐ ┌─────▼──────┐
          │ PostgreSQL │ │ Redis │ │Gemini │ │LINE API    │
          │ Database   │ │ Cache │ │AI API │ │            │
          └────────────┘  └───────┘ └───────┘ └────────────┘
                                        │
                                 ┌──────┴──────┐
                                 │             │
                            ┌────▼────┐ ┌─────▼─────┐
                            │Stock API│ │Google News│
                            └─────────┘ └───────────┘
```

**系統介面**:

- **前端 ↔ 後端**: HTTP/HTTPS REST API + WebSocket
- **後端 ↔ 資料庫**: PostgreSQL (asyncpg)
- **後端 ↔ 快取**: Redis
- **後端 ↔ AI**: Google Gemini API (HTTPS)
- **後端 ↔ LINE**: LINE Messaging API (HTTPS)
- **後端 ↔ 股價**: 台灣證交所 API / Yahoo Finance (HTTPS)

### 2.2 Product Functions (產品功能總覽)

主要功能模組：

1. **用戶管理模組** (REQ-010 ~ REQ-019)
   - 用戶註冊與登入 (JWT認證)
   - 密碼管理與安全
   - 用戶設定檔管理

2. **股價監控模組** (REQ-020 ~ REQ-039)
   - 即時股價更新
   - 關注清單管理
   - K線圖繪製
   - 技術指標計算

3. **新聞爬蟲模組** (REQ-040 ~ REQ-049)
   - Google News 爬取
   - 情緒分析
   - 新聞分類

4. **社群分析模組** (REQ-050 ~ REQ-059)
   - PTT/Dcard 爬取
   - 情緒趨勢分析

5. **AI 分析模組** (REQ-060 ~ REQ-069)
   - Gemini API 整合
   - 投資建議生成
   - 風險評估

6. **通知服務模組** (REQ-070 ~ REQ-079)
   - LINE 通知推送
   - 通知偏好設定
   - 通知歷史記錄

7. **報表生成模組** (REQ-080 ~ REQ-089)
   - 日/週/月/年報自動生成
   - 視覺化圖表
   - PDF 匯出

8. **審計日誌模組** (REQ-090 ~ REQ-099)
   - 操作記錄
   - 錯誤追蹤

### 2.3 User Classes and Characteristics (用戶類別與特徵)

| 用戶類別 | 描述 | 技術能力 | 使用頻率 | 權限等級 |
|---------|------|---------|---------|---------|
| **新手投資者** | 主要目標用戶，零基礎投資者 | 基礎電腦操作 | 每日 | User |
| **系統管理員** | 系統維護與監控 | 高級技術背景 | 按需 | Admin |

### 2.4 Operating Environment (運行環境)

**開發環境**:

- OS: Windows 10+, macOS 10.15+, Ubuntu 20.04+
- Python: 3.11+
- Node.js: 18+  
- PostgreSQL: 15+
- Redis: 7+

**生產環境**:

- 部署方式: Docker Compose / 本地安裝
- 最低硬體: 2 Core CPU, 4GB RAM, 20GB SSD
- 網路: 10 Mbps

**客戶端環境**:

- 瀏覽器: Chrome 90+, Firefox 90+, Safari 14+, Edge 90+
- 解析度: 1280x720 以上
- 網路: 5 Mbps 以上

### 2.5 Design and Implementation Constraints (設計與實作約束)

參考 PRD Section 5.2 約束條件：

- 技術約束 (TC-01 ~ TC-06)
- 資源約束 (RC-01 ~ RC-05)
- 法規約束 (LC-01 ~ LC-05)
- 時間約束 (TM-01 ~ TM-04)

### 2.6 Assumptions and Dependencies (假設與依賴)

參考 PRD Section 5.3：

- 假設條件 (AS-01 ~ AS-08)
- 外部依賴 (ED-01 ~ ED-05)  
- 內部依賴 (ID-01 ~ ID-04)

---

## 3. Specific Requirements (詳細需求)

### 3.1 External Interface Requirements (外部介面需求)

#### 3.1.1 User Interfaces (用戶介面)

**REQ-001: Web 應用主介面**

- **描述**: 提供 React 單頁應用 (SPA) 作為主要用戶介面
- **追溯**: FR-18, US-01
- **詳細規格**:
  - 響應式設計，支援桌面與行動版 view
  - Material-UI 或類似現代設計語言
  - 深色/淺色主題切換
  - 頁面載入時間 < 3 秒
- **驗收準則**:
  - [ ] 在 Chrome/Firefox/Safari 正確渲染
  - [ ] Lighthouse Performance Score > 80
  - [ ] 支援鍵盤導航 (無障礙)

**REQ-002: 儀表板介面**

- **描述**: 股票監控儀表板，顯示關注清單與即時股價
- **追溯**: FR-01, US-01, US-02
- **UI 元素**:
  - 股票卡片（股票代碼、名稱、價格、漲跌幅）
  - 即時更新指示器
  - 搜尋框（新增股票）
  - 排序/過濾選項
- **驗收準則**:
  - [ ] 顯示至少 10 支股票無卡頓
  - [ ] WebSocket 即時更新延遲 < 1 秒

**REQ-003: 圖表介面**

- **描述**: K線圖與技術指標圖表
- **追溯**: FR-03, US-03
- **圖表庫**: Recharts 或 Chart.js
- **功能**:
  - 日/週/月/年 K線切換
  - 移動平均線 (MA) 覆蓋
  - MACD/RSI/KD 指標顯示
  - 縮放與拖曳
- **驗收準則**:
  - [ ] 渲染 1000 個資料點 < 2 秒
  - [ ] 圖表互動流暢 (60 FPS)

**REQ-004: 報表檢視介面**

- **描述**: 報表列表與詳細檢視頁面
- **追溯**: FR-15, FR-16, US-10
- **功能**:
  - 報表列表（日期、類型、狀態）
  - 報表詳細內容（圖表+文字分析）
  - PDF 下載按鈕
- **驗收準則**:
  - [ ] 支援分頁（每頁 20 筆）
  - [ ] PDF 正確包含所有圖表

#### 3.1.2 Hardware Interfaces (硬體介面)

無特定硬體介面需求。系統運行於標準伺服器硬體。

#### 3.1.3 Software Interfaces (軟體介面)

**REQ-005: PostgreSQL 資料庫介面**

- **版本**: PostgreSQL 15+
- **連接方式**: asyncpg (非同步連接)
- **連接池**: 最小 5 連線，最大 20 連線
- **字元編碼**: UTF-8
- **時區**: UTC (統一使用 UTC，前端轉換為 UTC+8)

**REQ-006: Redis 快取介面**

- **版本**: Redis 7+
- **用途**: 股價快取、Session 儲存
- **過期策略**: LRU (Least Recently Used)
- **資料格式**: JSON 字串

**REQ-007: Google Gemini API 介面**

- **API 版本**: v1
- **模型**: gemini-pro
- **請求格式**: JSON over HTTPS
- **認證**: API Key
- **超時設定**: 10 秒
- **錯誤處理**: 實作重試機制（最多 3 次）

**REQ-008: LINE Messaging API 界面**

- **API 版本**: Messaging API v2
- **認證**: Channel Access Token
- **訊息類型**: Text Message + Flex Message
- **Webhook**: 接收用戶訊息（未來擴展）

**REQ-009: 股價資料 API 介面**

- **主要來源**: Yahoo Finance API
- **備援來源**: FinMind API
- **更新頻率**: 盤中每 2 秒
- **資料格式**: JSON
- **錯誤處理**: 自動切換備援 API

#### 3.1.4 Communications Interfaces (通訊介面)

**REQ-010: HTTP/HTTPS 通訊**

- **協議**: HTTPS (TLS 1.2+) 生產環境
- **HTTP 方法**: GET, POST, PUT, DELETE, PATCH
- **內容格式**: JSON (application/json)
- **CORS**: 允許指定來源

**REQ-011: WebSocket 通訊**

- **用途**: 即時股價推送
- **協議**: WSS (WebSocket Secure) 生產環境
- **心跳間隔**: 30 秒
- **重連機制**: 指數退避（最多 5 次）

---

### 3.2 Functional Requirements (功能需求)

由於篇幅限制，以下為關鍵功能需求。完整需求見附錄 A。

#### 3.2.1 用戶管理 (REQ-012 ~ REQ-019)

**REQ-012: 用戶註冊**

- **描述**: 新用戶註冊帳號
- **追溯**: FR-19, US-12
- **輸入**: Email, 密碼, 用戶名稱
- **處理邏輯**:
  1. 驗證 Email 格式（RFC 5322）
  2. 驗證密碼強度（≥8字元, 含大小寫數字）
  3. 檢查 Email 唯一性
  4. 使用 bcrypt 加密密碼（rounds=10）
  5. 生成 UUID user_id
  6. 插入資料庫 users 表
- **輸出**: 成功: user_id + JWT Token, 失敗: 錯誤訊息
- **例外處理**: Email 重複 → HTTP 409 Conflict

**REQ-013: 用戶登入**

- **描述**: 現有用戶登入系統
- **追溯**: FR-19, US-12
- **輸入**: Email, 密碼
- **處理邏輯**:
  1. 查詢資料庫取得用戶資料
  2. 驗證密碼（bcrypt.verify）
  3. 檢查帳號狀態（is_active）
  4. 生成 JWT Access Token（30分鐘）
  5. 生成 Refresh Token（7天）
  6. 記錄審計日誌
- **輸出**: JWT Token + Refresh Token
- **例外處理**:
  - 用戶不存在 → HTTP 401
  - 密碼錯誤 → HTTP 401
  - 帳號鎖定 → HTTP 403

**REQ-014: JWT Token 驗證**

- **描述**: 驗證每個 API 請求的 JWT Token
- **追溯**: NFR-09, NFR-10
- **輸入**: Authorization: Bearer {token}
- **處理邏輯**:
  1. 從 Header 提取 Token
  2. 驗證簽名（HMAC-SHA256）
  3. 檢查過期時間
  4. 提取 user_id 與 role
- **輸出**: 驗證成功: user_id, 失敗: HTTP 401
- **效能需求**: 驗證時間 < 5ms

#### 3.2.2 股價監控 (REQ-020 ~ REQ-039)

**REQ-020: 即時股價更新**

- **描述**: 後端定期從外部 API 取得股價並推送至前端
- **追溯**: FR-01, US-01
- **輸入**: 關注清單中的股票代碼列表
- **處理邏輯**:
  1. 每 2 秒執行一次（盤中時段）
  2. 批量查詢股價 API（最多 50 支一次）
  3. 解析 JSON 回應
  4. 計算漲跌幅與漲跌金額
  5. 更新 Redis 快取（TTL 60 秒）
  6. 透過 WebSocket 推送至連線的前端
  7. 儲存歷史記錄至 price_histories 表
- **輸出**: WebSocket 訊息 {stock_code, price, change, time}
- **效能需求**:
  - API 查詢時間 < 1 秒
  - WebSocket 推送延遲 < 500ms
- **錯誤處理**:
  - API 失敗 → 切換備援 API
  - 連續失敗 3 次 → 發送系統通知

**REQ-021: 關注清單管理 - 新增股票**

- **描述**: 用戶新增股票至關注清單
- **追溯**: FR-02, US-02
- **輸入**: stock_code (例: "2330")
- **處理邏輯**:
  1. 驗證股票代碼格式（台股：4或6位數字）
  2. 查詢 stocks 表確認股票存在
  3. 檢查用戶關注清單數量（最多 50）
  4. 檢查是否已在清單中
  5. 插入 watchlists 表
- **輸出**: 成功: watchlist_id, 失敗: 錯誤訊息
- **業務規則**: BR-01

**REQ-022: K線圖資料查詢**

- **描述**: 查詢指定股票的歷史 K線資料
- **追溯**: FR-03, US-03
- **輸入**: stock_code, period (day/week/month), start_date, end_date
- **處理邏輯**:
  1. 從 price_histories 表查詢
  2. 根據 period 聚合資料
  3. 計算 OHLC (開/高/低/收)
  4. 返回 JSON 陣列
- **輸出**: [{date, open, high, low, close, volume}]
- **效能需求**: 查詢 1 年資料 < 1 秒

#### 3.2.3 AI 分析 (REQ-060 ~ REQ-069)

**REQ-060: AI 投資建議生成**

- **描述**: 呼叫 Gemini API 生成投資建議
- **追溯**: FR-08, US-06
- **輸入**: stock_code
- **處理邏輯**:
  1. 收集多維度資料：
     - 過去 30 天股價趨勢
     - 最近 7 天相關新聞（含情緒分數）
     - 技術指標（MA, MACD, RSI）
  2. 組織結構化 Prompt
  3. 呼叫 Gemini API (gemini-pro)
  4. 解析 AI 回應
  5. 提取 recommendation (買入/持有/賣出) + reasoning
  6. 儲存至 ai_analyses 表
- **輸出**: {recommendation, confidence, reasoning, created_at}
- **效能需求**: P95 < 5 秒
- **業務規則**: BR-03 (每日限制 20 次)

---

### 3.3 Non-Functional Requirements (非功能需求)

#### 3.3.1 Performance Requirements (效能需求)

**REQ-070: API 響應時間**

- **P50**: < 500ms
- **P95**: < 2 秒
- **P99**: < 5 秒
- **測量方式**: APM 工具（Sentry / New Relic）

**REQ-071: 股價更新延遲**

- **盤中時段**: < 2 秒（從 API 取得到 WebSocket 推送）
- **測量方式**: 時間戳記差

**REQ-072: 並發用戶支援**

- **目標**: 同時支援 1000 個併發用戶
- **測試方式**: Locust 壓力測試

**REQ-073: 資料庫查詢效能**

- **簡單查詢** (SELECT by PK): < 10ms
- **複雜查詢** (JOIN + Aggregation): < 500ms
- **歷史資料查詢** (1 年): < 1 秒

**REQ-074: 前端頁面載入**

- **首次載入**: < 3 秒
- **後續導航**: < 1 秒
- **測量工具**: Lighthouse

#### 3.3.2 Safety Requirements (安全性需求)

**REQ-075: 資料備份**

- **頻率**: 每日自動備份
- **保留期限**: 30 天
- **儲存位置**: 與主資料庫分離的儲存

**REQ-076: 災難復原**

- **RTO** (Recovery Time Objective): 4 小時
- **RPO** (Recovery Point Objective): 24 小時

#### 3.3.3 Security Requirements (安全需求)

參考 `docs/SECURITY.md`

**REQ-077: 密碼加密**

- **演算法**: bcrypt
- **Salt rounds**: 10
- **不得以明文儲存**

**REQ-078: HTTPS 強制**

- **生產環境**: 強制使用 HTTPS
- **TLS 版本**: TLS 1.2+
- **憑證**: Let's Encrypt 或 CA 簽發

**REQ-079: SQL Injection 防護**

- **方法**: 使用 ORM (SQLAlchemy) 參數化查詢
- **禁止**: 字串拼接 SQL

**REQ-080: XSS 防護**

- **前端**: React 自動轉義 + DOMPurify
- **後端**: HTML 編碼輸出

**REQ-081: CSRF 防護**

- **方法**: SameSite Cookie + CSRF Token

**REQ-082: Rate Limiting**

- **API 全域限制**: 60 requests/minute/IP
- **登入端點**: 5 requests/minute/IP
- **AI 分析**: 20 requests/day/user

#### 3.3.4 Software Quality Attributes (軟體品質屬性)

**REQ-083: 可用性 (Availability)**

- **目標 Uptime**: > 99.5% (約每月停機 < 3.6 小時)
- **計劃性維護**: 於非交易時間進行

**REQ-084: 可維護性 (Maintainability)**

- **代碼覆蓋率**: > 70%
- **代碼規範**: PEP 8 (Python), ESLint (JavaScript)
- **API 文檔**: Swagger 自動生成

**REQ-085:可擴展性 (Scalability)**

- **水平擴展**: 無狀態後端設計，支援多實例
- **資料庫**: 支援 Read Replica

**REQ-086: 可用性 (Usability)**

- **新手上手時間**: < 10 分鐘完成註冊與新增股票
- **錯誤訊息**: 清晰易懂，提供解決建議

---

### 3.4 Logical Database Requirements (邏輯資料庫需求)

**REQ-087: 資料庫選擇**

- **DBMS**: PostgreSQL 15+
- **字元編碼**: UTF-8
- **時區**: UTC

**REQ-088: 資料表設計**

參考 `docs/diagrams/database-er.puml` 與 `docs/DB_SCHEMA.md`

核心資料表：

- users（用戶資料）
- stocks（股票基本資料）
- watchlists（關注清單）
- price_histories（歷史股價）
- news（新聞）
- ai_analyses（AI 分析結果）
- notifications（通知記錄）

**REQ-089: 資料完整性**

- **主鍵**: 所有表使用 UUID 作為主鍵
- **外鍵**: 強制參照完整性約束
- **NOT NULL**: 必要欄位設定 NOT NULL
- **UNIQUE**: Email 等唯一性欄位

**REQ-090: 索引設計**

- **主鍵索引**: 自動建立
- **外鍵索引**: 手動建立加速 JOIN
- **查詢優化索引**: created_at, stock_code 等常查詢欄位

**REQ-091: 資料備份與遷移**

- **遷移工具**: Alembic
- **版本控制**: 所有 schema 變更納入版本控制

---

### 3.5 Design Constraints (設計約束)

**REQ-092: 架構模式**

- **後端**: 採用 DDD (Domain-Driven Design) 分層架構
- **前端**: 採用 React Hooks + Context API

**REQ-093: 技術棧限制**

- **後端框架**: FastAPI（不可更換）
- **前端框架**: React（不可更換）
- **資料庫**: PostgreSQL（不可更換）

**REQ-094: API 設計規範**

- **風格**: RESTful API
- **版本化**: /api/v1/ 前綴
- **回應格式**: 統一 JSON

**REQ-095: 錯誤處理規範**

參考 `docs/ERROR_HANDLING.md`

- **錯誤碼**: 統一錯誤碼系統（AUTH_401_001 格式）
- **trace_id**: 所有錯誤包含 trace_id

---

## 4. Supporting Information (支援資訊)

### 4.1 Requirements Traceability Matrix (RTM - 需求追溯矩陣)

#### 用戶故事 → 功能需求 → 技術需求 映射表

| User Story | Functional Requirement | Technical Requirements | 描述 |
|-----------|------------------------|------------------------|------|
| **US-01** | FR-01 | REQ-020, REQ-021, REQ-002 | 即時股價查看 |
| **US-02** | FR-02 | REQ-021, REQ-023 | 關注清單管理 |
| **US-03** | FR-03 | REQ-022, REQ-003 | K線圖與技術指標 |
| **US-04** | FR-04, FR-05 | REQ-030, REQ-031 | 新聞爬取與情緒分析 |
| **US-05** | FR-06, FR-07 | REQ-032, REQ-033 | 社群爬取與分析 |
| **US-06** | FR-08 | REQ-060, REQ-061 | AI 投資建議 |
| **US-07** | FR-09 | REQ-062 | 風險評估 |
| **US-08** | FR-10, FR-11, FR-12 | REQ-035, REQ-036 | 技術指標計算 |
| **US-09** | FR-13, FR-14 | REQ-070, REQ-071 | LINE 通知 |
| **US-10** | FR-15, FR-16 | REQ-080, REQ-081 | 多期報表 |
| **US-11** | FR-17 | REQ-082, REQ-004 | 報表視覺化 |
| **US-12** | FR-19, FR-20 | REQ-012, REQ-013, REQ-014 | 用戶註冊與登入 |
| **US-13** | FR-21 | REQ-090, REQ-091 | 審計日誌 |

#### 完整 RTM (部分展示)

```
US-01 (即時股價)
  └─ FR-01 (即時股價數據更新)
      ├─ REQ-020: 即時股價更新
      ├─ REQ-002: 儀表板介面
      └─ REQ-071: 股價更新延遲 < 2秒

US-06 (AI 分析)
  └─ FR-08 (AI 投資建議)
      ├─ REQ-060: AI 投資建議生成
      ├─ REQ-007: Gemini API 介面
      ├─ REQ-070: API 響應時間 < 5秒
      └─ BR-03: 每日請求限制 20 次

US-12 (用戶登入)
  └─ FR-19 (用戶認證)
      ├─ REQ-012: 用戶註冊
      ├─ REQ-013: 用戶登入
      ├─ REQ-014: JWT Token 驗證
      ├─ REQ-077: 密碼加密
      └─ REQ-082: Rate Limiting
```

---

## 5. Appendices (附錄)

### 5.1 完整功能需求清單

由於篇幅限制，完整清單包含 REQ-001 ~ REQ-100。請參考：

- `docs/SDD.md` - 軟體設計文檔（詳細設計）
- `docs/API.md` - API 端點詳細規格

### 5.2 測試需求

所有 REQ 需求必須：

- 包含單元測試（覆蓋率 > 70%）
- 通過整合測試
- 符合 AC 驗收標準

### 5.3 變更歷史

| 日期 | 版本 | 變更項目 | 變更者 |
|------|------|---------|--------|
| 2026-01-29 | 1.0 | 初始版本 | Development Team |

---

**文檔結束**

**維護者**: AuraTrade Development Team  
**最後更新**: 2026-01-29  
**狀態**: ✅ 已審查並核准
