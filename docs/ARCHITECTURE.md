# AuraTrade 系統架構概覽

## 🎯 文檔目的

本文檔提供 AuraTrade 系統的高層次架構視圖，幫助開發者快速理解系統整體設計。

---

## 🏗️ 系統架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                        User Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Web App  │  │ Mobile   │  │  LINE    │                  │
│  │ (React)  │  │   App    │  │  Bot     │                  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
└───────┼─────────────┼─────────────┼─────────────────────────┘
        │             │             │
        └─────────────┴─────────────┘
                      │
        ┌─────────────▼──────────────┐
        │     API Gateway             │
        │   (Rate Limiting, Auth)     │
        └─────────────┬───────────────┘
                      │
        ┌─────────────▼──────────────┐
        │    Backend Services         │
        │     (FastAPI)               │
        │                             │
        │  ┌─────────────────────┐   │
        │  │   API Layer         │   │
        │  │  - Routes           │   │
        │  │  - Schemas          │   │
        │  │  - Middleware       │   │
        │  └──────────┬──────────┘   │
        │             │               │
        │  ┌──────────▼──────────┐   │
        │  │  Service Layer      │   │
        │  │  - Business Logic   │   │
        │  │  - External APIs    │   │
        │  │  - AI Integration   │   │
        │  └──────────┬──────────┘   │
        │             │               │
        │  ┌──────────▼──────────┐   │
        │  │ Repository Layer    │   │
        │  │  - Data Access      │   │
        │  │  - ORM Models       │   │
        │  └──────────┬──────────┘   │
        └─────────────┼───────────────┘
                      │
        ┌─────────────▼──────────────┐
        │   Data Layer                │
        │  ┌──────────┐  ┌─────────┐ │
        │  │PostgreSQL│  │  Redis  │ │
        │  │          │  │ (Cache) │ │
        │  └──────────┘  └─────────┘ │
        └─────────────────────────────┘
                      │
        ┌─────────────▼──────────────┐
        │  External Services          │
        │  ┌──────────┐  ┌─────────┐ │
        │  │ Google   │  │  LINE   │ │
        │  │ Gemini   │  │   API   │ │
        │  └──────────┘  └─────────┘ │
        │  ┌──────────┐  ┌─────────┐ │
        │  │Stock API │  │ News API│ │
        │  └──────────┘  └─────────┘ │
        └─────────────────────────────┘
```

---

## 🎨 前端架構

### 技術棧

- **框架**: React 18+
- **語言**: TypeScript
- **打包工具**: Vite
- **狀態管理**: Zustand / Redux Toolkit
- **UI 框架**: Material-UI / TailwindCSS
- **圖表**: Recharts / Chart.js
- **HTTP 客戶端**: Axios
- **即時通訊**: WebSocket

### 目錄結構

```
frontend/src/
├── components/      # React 元件
│   ├── common/      # 共用元件
│   ├── features/    # 功能元件
│   └── layouts/     # 版面配置
├── pages/           # 頁面元件
├── hooks/           # 自定義 Hooks
├── services/        # API 服務
├── stores/          # 狀態管理
├── utils/           # 工具函數
└── types/           # TypeScript 型別
```

---

## ⚙️ 後端架構 (DDD 分層)

### 技術棧

- **框架**: FastAPI
- **語言**: Python 3.11+
- **ORM**: SQLAlchemy 2.0
- **資料庫**: PostgreSQL 15
- **快取**: Redis
- **任務佇列**: Celery / APScheduler
- **認證**: JWT (jose)
- **驗證**: Pydantic

### DDD 分層設計

#### 1. API Layer (表現層)

**職責**: 處理 HTTP 請求與回應

- Routes: 定義 API 端點
- Schemas: Pydantic 資料驗證
- Middleware: 認證、CORS、錯誤處理

#### 2. Service Layer (應用層)

**職責**: 業務流程協調

- 協調多個 Repository
- 調用外部 API (Gemini, LINE, 股價)
- 事務管理
- 業務規則驗證

#### 3. Domain Layer(領域層)

**職責**: 核心業務邏輯

- Entity: 領域實體 (Stock, User, News)
- Value Object: 值對象
- Domain Logic: 業務規則方法

#### 4. Repository Layer (基礎設施層)

**職責**: 資料持久化

- CRUD 操作
- 複雜查詢封裝
- ORM 操作

### 目錄結構

```
backend/apps/
├── api/
│   └── v1/
│       ├── routes/      # API 路由
│       ├── schemas/     # Pydantic Schemas
│       └── middleware/  # 中介軟體
├── services/            # 業務邏輯層
├── repositories/        # 資料存取層
├── models/              # ORM 模型
├── core/                # 核心配置
│   ├── config.py
│   ├── security.py
│   └── database.py
└── tasks/               # 背景任務
    ├── crawlers/        # 爬蟲
    └── schedulers/      # 排程
```

---

## 💾 資料庫設計

### 核心資料表

- **users**: 用戶資料
- **stocks**: 股票基本資料
- **watchlists**: 關注清單
- **price_histories**: 歷史股價
- **news**: 新聞資料
- **ai_analyses**: AI 分析結果
- **notifications**: 通知記錄

### 資料關聯

```
users (1) ──── (N) watchlists ──── (N) stocks
users (1) ──── (N) notifications
stocks (1) ──── (N) price_histories
stocks (1) ──── (N) news
stocks (1) ──── (N) ai_analyses
```

---

## 🔄 資料流程

### 1. 股價更新流程

```
Stock API → Crawler → Service → Repository → Database
                ↓
              Cache (Redis)
                ↓
         WebSocket → Frontend
```

### 2. AI 分析流程

```
User Request → API → Service → Gemini API
                                    ↓
                              AI Analysis
                                    ↓
                         Save to Database
                                    ↓
                          Return to User
```

### 3. LINE 通知流程

```
Price Alert Triggered → Service → LINE API → User
```

---

## 🔐 安全架構

### 認證流程

```
1. User Login → Verify Credentials
2. Generate JWT (Access + Refresh Token)
3. Store Refresh Token in HttpOnly Cookie
4. Return Access Token
5. Client stores Access Token in Memory
6. Every Request: Send Access Token in Header
7. Backend: Verify Token → Return Data
```

### 授權層級

- **Admin**: 所有權限
- **User**: 一般用戶權限
- **ReadOnly**: 唯讀權限(未來)

---

## 📊 監控與日誌

### 監控指標

- **系統**: CPU, Memory, Disk
- **應用**: API 響應時間, 錯誤率, QPS
- **業務**: 活躍用戶數, 股價更新延遲

### 日誌收集

```
Application → Structured JSON Logs → ELK Stack
                                         ↓
                                    Kibana Dashboard
```

### APM 工具

- **錯誤追蹤**: Sentry
- **效能監控**: New Relic / Datadog

---

## 🚀 部署架構

### 開發環境

```
Developer Machine
├── Frontend (localhost:5173)
├── Backend (localhost:8000)
└── PostgreSQL (localhost:5432)
```

### 生產環境 (藍綠部署)

```
Load Balancer (nginx)
    ├── Blue Environment (Active)
    │   ├── Frontend Container (x3)
    │   └── Backend Container (x3)
    └── Green Environment (Standby)
        ├── Frontend Container (x3)
        └── Backend Container (x3)

Database Cluster
├── Primary PostgreSQL
└── Replica (Read-Only)

Cache Layer
└── Redis Cluster
```

---

## 🔧 第三方服務整合

| 服務 | 用途 | 整合方式 |
|------|------|----------|
| Google Gemini | AI 分析與建議 | REST API |
| LINE Messaging API | 通知推送 | Webhook + REST API |
| 股價資料 API | 即時股價 | REST API / WebSocket |
| Google News | 新聞爬取 | Web Scraping |
| PTT爬蟲 | 社群情緒分析 | Web Scraping |

---

## 📱 支援的客戶端

### Phase 1 (MVP)

- ✅ Web App (Desktop + Mobile responsive)
- ✅ LINE Bot

### Phase 2 (未來)

- ⏳ iOS Native App
- ⏳ Android Native App

---

## 🎯 效能目標

| 指標 | 目標值 | 監控方式 |
|------|--------|----------|
| API 響應時間 (P95) | < 2s | APM |
| API 響應時間 (P99) | < 5s | APM |
| 股價更新延遲 | < 2s | 業務監控 |
| 系統可用性 | > 99.5% | UptimeRobot |
| 錯誤率 | < 1% | Sentry |

---

## 📈 擴展性設計

### 水平擴展

- Frontend: CDN + 靜態檔案快取
- Backend: 無狀態設計，可水平擴展
- Database: Read Replica 讀寫分離

### 垂直擴展

- 資料庫升級硬體
- Redis 記憶體擴充

---

## 📚 相關文檔

- [系統設計文檔 (SDD)](./SDD.md)
- [API 文檔](./API.md)
- [資料庫 Schema](./DB_SCHEMA.md)
- [安全規範](./SECURITY.md)
- [部署指南](./DEPLOYMENT.md)

---

**最後更新**: 2026-01-29  
**版本**: 1.0  
**維護者**: AuraTrade Architecture Team
