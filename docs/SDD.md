# AuraTrade 軟體設計文檔 (SDD)

## 文檔版本控制

| 版本 | 日期 | 作者 | 變更描述 |
|------|------|------|----------|
| 1.0 | 2026-01-29 | Architecture Team | 初始版本 - 基於 SRS v1.0 |

---

## 1. Introduction (簡介)

### 1.1 Purpose (目的)

本軟體設計文檔 (SDD) 定義 AuraTrade 系統的完整架構設計與詳細設計規格。

**目標讀者**：

- 系統架構師
- 開發團隊（前端、後端、全端工程師）
- DevOps 工程師
- 技術審查人員

### 1.2 Scope (範圍)

本文檔涵蓋：

- 系統整體架構設計
- DDD 分層架構詳細設計
- 資料庫設計（含 ER 圖）
- API 設計規範
- 安全設計策略
- 效能設計方案
- 部署架構

### 1.3 Definitions and Acronyms (定義與縮寫)

參考 `docs/SRS.md` Section 1.3

### 1.4 References (參考文獻)

- **PRD**: `docs/PRD.md` - 產品需求文檔 v1.0
- **SRS**: `docs/SRS.md` - 軟體需求規格書 v1.0
- **ARCHITECTURE**: `docs/ARCHITECTURE.md` - 系統架構概覽
- **UML 圖表**: `docs/diagrams/` - PlantUML 圖表集
- **Eric Evans - Domain-Driven Design**: 領域驅動設計參考書

---

## 2. System Overview (系統概述)

### 2.1 System Context (系統上下文)

AuraTrade 是一個**三層架構**的 Web 應用系統：

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│                     (React Frontend)                         │
│  - User Interface Components                                │
│  - State Management (Zustand/Redux)                         │
│  - HTTP Client (Axios)                                       │
└────────────────────┬─────────────────────────────────────────┘
                     │ HTTP/HTTPS + WebSocket
┌────────────────────▼─────────────────────────────────────────┐
│                   Application Layer                          │
│                   (FastAPI Backend)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           API Layer (Routes + Schemas)                │  │
│  └──────────────────┬───────────────────────────────────┘  │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │         Service Layer (Business Logic)               │  │
│  └──────────────────┬───────────────────────────────────┘  │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │      Repository Layer (Data Access)                  │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│                     Data Layer                               │
│  ┌──────────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │ PostgreSQL   │  │  Redis   │  │ External Services    │  │
│  │  Database    │  │  Cache   │  │ (Gemini/LINE/Stock)  │  │
│  └──────────────┘  └──────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

參考完整架構圖：[architecture.puml](./diagrams/architecture.puml)

![系統架構圖](./diagrams/architecture.svg)

### 2.2 Design Principles (設計原則)

#### 2.2.1 SOLID 原則

- **S**ingle Responsibility: 每個類/模組只有一個職責
- **O**pen/Closed: 對擴展開放，對修改關閉
- **L**iskov Substitution: 子類可替換父類
- **I**nterface Segregation: 介面隔離，不強迫實作不需要的方法
- **D**ependency Inversion: 依賴抽象而非具體實作

#### 2.2.2 DDD 原則

- **Ubiquitous Language**: 統一語言（業務與技術團隊使用相同術語）
- **Bounded Context**: 限界上下文（明確模組邊界）
- **Domain Model**: 領域模型（反映業務邏輯）
- **Layered Architecture**: 分層架構（隔離業務邏輯與基礎設施）

#### 2.2.3 RESTful API 設計原則

- 資源導向（Resource-oriented）
- 使用標準 HTTP 方法（GET/POST/PUT/DELETE）
- 無狀態（Stateless）
- 統一介面（Uniform Interface）

---

## 3. Architectural Strategies (架構策略)

### 3.1 Backend Architecture (後端架構)

#### 3.1.1 DDD 分層架構

```
backend/
├── apps/
│   ├── api/                    # API Layer
│   │   └── v1/
│   │       ├── routes/         # API 路由
│   │       │   ├── stocks.py
│   │       │   ├── auth.py
│   │       │   ├── ai.py
│   │       │   └── reports.py
│   │       ├── schemas/        # Pydantic Schemas
│   │       │   ├── stock.py
│   │       │   └── user.py
│   │       └── middleware/     # 中介軟體
│   │           ├── auth.py
│   │           ├── cors.py
│   │           └── error_handler.py
│   │
│   ├── services/               # Service Layer (業務邏輯)
│   │   ├── stock_service.py
│   │   ├── ai_service.py
│   │   ├── news_service.py
│   │   ├── auth_service.py
│   │   └── report_service.py
│   │
│   ├── repositories/           # Repository Layer (資料存取)
│   │   ├── stock_repository.py
│   │   ├── user_repository.py
│   │   ├── news_repository.py
│   │   └── watchlist_repository.py
│   │
│   ├── models/                 # ORM Models (SQLAlchemy)
│   │   ├── stock.py
│   │   ├── user.py
│   │   ├── news.py
│   │   └── watchlist.py
│   │
│   ├── core/                   # Core Configuration
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   └── exceptions.py
│   │
│   └── tasks/                  # Background Tasks
│       ├── crawlers/
│       │   ├── stock_crawler.py
│       │   ├── news_crawler.py
│       │   └── social_crawler.py
│       └── schedulers/
│           ├── report_scheduler.py
│           └── price_updater.py
│
└── tests/                      # 測試
    ├── unit/
    ├── integration/
    └── e2e/
```

#### 3.1.2 層級職責詳解

**API Layer (表現層)**

職責：

- 處理 HTTP 請求與回應
- 請求驗證（Pydantic Schemas）
- 認證與授權（JWT）
- 錯誤處理與轉換
- API 文檔生成（Swagger）

範例：

```python
# apps/api/v1/routes/stocks.py
from fastapi import APIRouter, Depends
from apps.api.v1.schemas.stock import StockPriceResponse
from apps.services.stock_service import StockService
from apps.api.v1.middleware.auth import get_current_user

router = APIRouter()

@router.get("/stocks/{stock_code}/price", response_model=StockPriceResponse)
async def get_stock_price(
    stock_code: str,
    stock_service: StockService = Depends(),
    current_user = Depends(get_current_user)
):
    """取得即時股價 - 追溯: REQ-020"""
    return await stock_service.get_real_time_price(stock_code)
```

**Service Layer (應用層/業務邏輯層)**

職責：

- 業務流程協調
- 調用多個 Repository
- 調用外部 API
- 事務管理
- 業務規則驗證

範例：

```python
# apps/services/stock_service.py
from apps.repositories.stock_repository import StockRepository
from apps.repositories.watchlist_repository import WatchlistRepository
from apps.core.exceptions import StockNotFoundError
import httpx

class StockService:
    def __init__(self):
        self.stock_repo = StockRepository()
        self.watchlist_repo = WatchlistRepository()
        self.cache = RedisCache()
    
    async def get_real_time_price(self, stock_code: str):
        """取得即時股價 - 追溯: REQ-020"""
        # 1. 檢查快取
        cached_price = await self.cache.get(f"stock_price:{stock_code}")
        if cached_price:
            return cached_price
        
        # 2. 查詢資料庫確認股票存在
        stock = await self.stock_repo.find_by_code(stock_code)
        if not stock:
            raise StockNotFoundError(code="STOCK_404_001", message=f"找不到股票代碼 {stock_code}")
        
        # 3. 調用外部 API
        price_data = await self._fetch_from_external_api(stock_code)
        
        # 4. 更新快取
        await self.cache.set(f"stock_price:{stock_code}", price_data, ttl=60)
        
        # 5. 儲存歷史記錄
        await self.stock_repo.save_price_history(stock_code, price_data)
        
        return price_data
```

**Repository Layer (基礎設施層/資料存取層)**

職責：

- 封裝資料庫操作（CRUD）
- ORM 物件操作
- 複雜查詢封裝
- 資料轉換（ORM ↔ Domain Model）

範例：

```python
# apps/repositories/stock_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from apps.models.stock import Stock
from sqlalchemy import select

class StockRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def find_by_code(self, stock_code: str) -> Stock:
        """根據股票代碼查詢 - 追溯: REQ-021"""
        result = await self.db.execute(
            select(Stock).where(Stock.stock_code == stock_code)
        )
        return result.scalar_one_or_none()
    
    async def save_price_history(self, stock_code: str, price_data: dict):
        """儲存股價歷史 - 追溯: REQ-020"""
        # 實作省略
        pass
```

**Models (ORM 模型)**

職責：

- 定義資料庫表結構
- 定義欄位約束
- 定義關聯關係

範例：

```python
# apps/models/stock.py
from sqlalchemy import Column, String, DECIMAL, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from apps.core.database import Base
import uuid

class Stock(Base):
    __tablename__ = "stocks"
    
    stock_code = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False)
    market = Column(String(20), nullable=False)
    industry = Column(String(50))
    created_at = Column(TIMESTAMP, default=func.now())
```

### 3.2 Frontend Architecture (前端架構)

```
frontend/src/
├── components/              # React 元件
│   ├── common/              # 共用元件
│   │   ├── Button/
│   │   ├── Input/
│   │   ├── Modal/
│   │   └── Loading/
│   ├── features/            # 功能元件
│   │   ├── stocks/
│   │   │   ├── StockCard.tsx
│   │   │   ├── StockList.tsx
│   │   │   └── StockChart.tsx
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   └── reports/
│   │       └── ReportView.tsx
│   └── layouts/             # 版面配置
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Footer.tsx
│
├── pages/                   # 頁面元件
│   ├── Dashboard.tsx
│   ├── StockDetail.tsx
│   ├── Reports.tsx
│   └── Settings.tsx
│
├── hooks/                   # 自定義 Hooks
│   ├── useAuth.ts
│   ├── useStockPrice.ts
│   └── useWebSocket.ts
│
├── services/                # API 服務
│   ├── api.ts               # Axios 配置
│   ├── stockApi.ts
│   ├── authApi.ts
│   └── reportApi.ts
│
├── stores/                  # 狀態管理
│   ├── authStore.ts
│   ├── stockStore.ts
│   └── uiStore.ts
│
├── utils/                   # 工具函數
│   ├── formatters.ts
│   ├── validators.ts
│   └── constants.ts
│
└── types/                   # TypeScript 型別
    ├── stock.ts
    ├── user.ts
    └── api.ts
```

---

## 4. System Architecture (系統架構)

### 4.1 Component Diagram (元件圖)

參考：[architecture.puml](./diagrams/architecture.puml)

主要元件：

1. **Web Application** (React)
   - 用戶介面渲染
   - 狀態管理
   - WebSocket 連接

2. **API Gateway** (FastAPI)
   - 請求路由
   - 認證與授權
   - Rate Limiting

3. **Stock Price Service**
   - 股價更新邏輯
   - 快取管理
   - WebSocket 推送

4. **AI Analysis Service**
   - Gemini API 整合
   - Prompt 組織
   - 結果解析

5. **Notification Service**
   - LINE Messaging API 整合
   - 通知規則判斷
   - 訊息佇列管理

### 4.2 Deployment Diagram (部署圖)

**開發環境**:

```
Developer Machine
├── React Dev Server (localhost:5173)
├── FastAPI Dev Server (localhost:8000)
├── PostgreSQL (localhost:5432)
└── Redis (localhost:6379)
```

**生產環境 (Docker Compose)**:

```
Load Balancer (nginx)
    │
    ├── Frontend Container (x2)
    │   └── nginx:alpine + React build
    │
    └── Backend Container (x3)
        └── Python 3.11 + FastAPI
            │
            ├── PostgreSQL Container
            │   └── postgres:15
            │
            └── Redis Container
                └── redis:7
```

### 4.3 Sequence Diagrams (序列圖)

#### 股價查詢流程

參考：[stock-price-flow.puml](./diagrams/stock-price-flow.puml)

![股價查詢流程](./diagrams/stock-price-flow.svg)

#### AI 分析流程

參考：[ai-analysis-flow.puml](./diagrams/ai-analysis-flow.puml)

![AI 分析流程](./diagrams/ai-analysis-flow.svg)

#### 認證流程

參考：[authentication-flow.puml](./diagrams/authentication-flow.puml)

![認證流程](./diagrams/authentication-flow.svg)

---

## 5. Data Design (資料設計)

### 5.1 Database ER Diagram (資料庫 ER 圖)

參考：[database-er.puml](./diagrams/database-er.puml)

![資料庫 ER 圖](./diagrams/database-er.svg)

### 5.2 Data Dictionary (資料字典)

#### users 表

| 欄位 | 型別 | 約束 | 描述 | 追溯 |
|------|------|------|------|------|
| user_id | UUID | PK | 用戶唯一識別碼 | REQ-012 |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 用戶 Email | REQ-012 |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt 加密密碼 | REQ-077 |
| username | VARCHAR(100) | NOT NULL | 用戶名稱 | REQ-012 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 註冊時間 | REQ-012 |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | 帳號狀態 | REQ-013 |
| last_login_at | TIMESTAMP | | 最後登入時間 | REQ-013 |

**索引**:

- PRIMARY KEY: `user_id`
- UNIQUE INDEX: `idx_users_email` ON `email`
- INDEX: `idx_users_created_at` ON `created_at`

#### stocks 表

| 欄位 | 型別 | 約束 | 描述 | 追溯 |
|------|------|------|------|------|
| stock_code | VARCHAR(10) | PK | 股票代碼 | REQ-020 |
| name | VARCHAR(100) | NOT NULL | 股票名稱 | REQ-020 |
| market | VARCHAR(20) | NOT NULL | 市場（上市/上櫃） | REQ-020 |
| industry | VARCHAR(50) | | 產業分類 | REQ-020 |
| created_at | TIMESTAMP | DEFAULT NOW() | 建立時間 | REQ-020 |

**索引**:

- PRIMARY KEY: `stock_code`
- INDEX: `idx_stocks_industry` ON `industry`

#### watchlists 表

| 欄位 | 型別 | 約束 | 描述 | 追溯 |
|------|------|------|------|------|
| watchlist_id | UUID | PK | 關注記錄 ID | REQ-021 |
| user_id | UUID | FK, NOT NULL | 用戶 ID | REQ-021 |
| stock_code | VARCHAR(10) | FK, NOT NULL | 股票代碼 | REQ-021 |
| added_at | TIMESTAMP | DEFAULT NOW() | 新增時間 | REQ-021 |
| notes | TEXT | | 用戶備註 | REQ-021 |

**索引**:

- PRIMARY KEY: `watchlist_id`
- UNIQUE INDEX: `idx_watchlist_user_stock` ON `(user_id, stock_code)`
- INDEX: `idx_watchlist_user` ON `user_id`

#### price_histories 表

| 欄位 | 型別 | 約束 | 描述 | 追溯 |
|------|------|------|------|------|
| price_id | UUID | PK | 價格記錄 ID | REQ-020 |
| stock_code | VARCHAR(10) | FK, NOT NULL | 股票代碼 | REQ-020 |
| price | DECIMAL(10,2) | NOT NULL | 收盤價 | REQ-020 |
| volume | BIGINT | | 成交量 | REQ-020 |
| change | DECIMAL(10,2) | | 漲跌金額 | REQ-020 |
| change_percent | DECIMAL(5,2) | | 漲跌幅 (%) | REQ-020 |
| recorded_at | TIMESTAMP | NOT NULL | 記錄時間 | REQ-020 |

**索引**:

- PRIMARY KEY: `price_id`
- INDEX: `idx_price_stock_time` ON `(stock_code, recorded_at DESC)`

#### ai_analyses 表

| 欄位 | 型別 | 約束 | 描述 | 追溯 |
|------|------|------|------|------|
| analysis_id | UUID | PK | 分析記錄 ID | REQ-060 |
| stock_code | VARCHAR(10) | FK, NOT NULL | 股票代碼 | REQ-060 |
| user_id | UUID | FK, NOT NULL | 請求用戶 | REQ-060 |
| recommendation | VARCHAR(20) | NOT NULL | 建議（買入/持有/賣出） | REQ-060 |
| confidence | DECIMAL(3,2) | | 信心度 (0-1) | REQ-060 |
| reasoning | TEXT | | AI 分析原因 | REQ-060 |
| created_at | TIMESTAMP | DEFAULT NOW() | 分析時間 | REQ-060 |

**索引**:

- PRIMARY KEY: `analysis_id`
- INDEX: `idx_analysis_user_time` ON `(user_id, created_at DESC)`
- INDEX: `idx_analysis_stock` ON `stock_code`

### 5.3 Data Migration Strategy (資料遷移策略)

**工具**: Alembic

**遷移流程**:

```bash
# 建立遷移腳本
alembic revision --autogenerate -m "create users table"

# 執行遷移
alembic upgrade head

# 回滾
alembic downgrade -1
```

**版本控制**:

- 所有 schema 變更納入 Git
- 遷移檔案路徑：`backend/alembic/versions/`

---

## 6. Component Design (元件設計)

### 6.1 Backend Components (後端元件)

#### 6.1.1 StockService 類別設計

```python
class StockService:
    """股價服務 - 追溯: FR-01, FR-02, FR-03"""
    
    def __init__(self, stock_repo: StockRepository, cache: RedisCache):
        self.stock_repo = stock_repo
        self.cache = cache
    
    async def get_real_time_price(self, stock_code: str) -> StockPrice:
        """取得即時股價 - 追溯: REQ-020"""
        pass
    
    async def get_price_history(self, stock_code: str, period: str) -> List[PriceHistory]:
        """取得歷史股價 - 追溯: REQ-022"""
        pass
    
    async def calculate_technical_indicators(self, stock_code: str) -> TechnicalIndicators:
        """計算技術指標 - 追溯: REQ-035"""
        pass
```

#### 6.1.2 AIService 類別設計

```python
class AIService:
    """AI 分析服務 - 追溯: FR-08"""
    
    def __init__(self, gemini_client: GeminiClient, stock_service: StockService):
        self.gemini = gemini_client
        self.stock_service = stock_service
    
    async def analyze_stock(self, stock_code: str, user_id: str) -> AIAnalysis:
        """生成 AI 投資建議 - 追溯: REQ-060"""
        # 1. 收集數據
        price_data = await self.stock_service.get_price_history(stock_code, "30d")
        news_data = await self.news_service.get_recent_news(stock_code, days=7)
        indicators = await self.stock_service.calculate_technical_indicators(stock_code)
        
        # 2. 組織 Prompt
        prompt = self._build_prompt(price_data, news_data, indicators)
        
        # 3. 調用 Gemini API
        response = await self.gemini.generate_content(prompt)
        
        # 4. 解析回應
        analysis = self._parse_response(response)
        
        # 5. 儲存記錄
        await self.analysis_repo.save(analysis)
        
        return analysis
```

### 6.2 Frontend Components (前端元件)

#### 6.2.1 StockCard 元件

```typescript
interface StockCardProps {
  code: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  onClick?: () => void;
}

const StockCard: React.FC<StockCardProps> = ({ code, name, price, change, changePercent, onClick }) => {
  const isPositive = change >= 0;
  
  return (
    <div className="stock-card" onClick={onClick}>
      <div className="stock-header">
        <span className="stock-code">{code}</span>
        <span className="stock-name">{name}</span>
      </div>
      <div className="stock-price">${price.toFixed(2)}</div>
      <div className={`stock-change ${isPositive ? 'positive' : 'negative'}`}>
        {isPositive ? '+' : ''}{change.toFixed(2)} ({changePercent.toFixed(2)}%)
      </div>
    </div>
  );
};
```

---

## 7. Interface Design (介面設計)

### 7.1 API Interface Specification (API 介面規格)

詳細規格參考：`docs/API.md`

**API 命名規範**:

- 使用小寫與連字號
- 使用名詞複數形式
- 版本化：`/api/v1/`

**範例 API**:

```
GET    /api/v1/stocks/{stock_code}/price          # 取得股價
POST   /api/v1/stocks/watchlist                   # 新增關注
DELETE /api/v1/stocks/watchlist/{watchlist_id}    # 刪除關注
GET    /api/v1/ai/analyze/{stock_code}            # AI 分析
POST   /api/v1/auth/login                         # 用戶登入
POST   /api/v1/auth/register                      # 用戶註冊
GET    /api/v1/reports                            # 取得報表列表
```

**標準回應格式**:

成功:

```json
{
  "data": {...},
  "message": "Success"
}
```

失敗:

```json
{
  "error": {
    "code": "STOCK_404_001",
    "message": "找不到股票代碼 2330",
    "trace_id": "uuid-1234",
    "path": "/api/v1/stocks/2330/price"
  }
}
```

### 7.2 Database Interface (資料庫介面)

**連接配置**:

```python
# apps/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/auratrade"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session
```

---

## 8. Security Design (安全設計)

詳細規格參考：`docs/SECURITY.md`

### 8.1 Authentication (認證)

**JWT Token 結構**:

```json
{
  "user_id": "uuid-1234",
  "email": "user@example.com",
  "role": "user",
  "exp": 1706515200
}
```

**Token 管理**:

- Access Token: 儲存於記憶體（前端）
- Refresh Token: 儲存於 HttpOnly Cookie
- Secret Key: 環境變數（至少 32 字元）

### 8.2 Authorization (授權)

**RBAC 角色定義**:

- **user**: 一般用戶（所有功能）
- **admin**: 系統管理員（管理功能）

**權限檢查**:

```python
@router.get("/admin/users")
async def list_users(current_user = Depends(require_role("admin"))):
    pass
```

### 8.3 Data Protection (資料保護)

- **密碼**: bcrypt 加密
- **API Key**: 環境變數，不提交 Git
- **敏感日誌**: 脫敏處理（mask email/password）
- **HTTPS**: 生產環境強制

---

## 9. Performance Design (效能設計)

### 9.1 Caching Strategy (快取策略)

**Redis 快取**:

```python
# 股價快取（TTL 60 秒）
cache_key = f"stock_price:{stock_code}"
await redis.set(cache_key, json.dumps(price_data), ex=60)

# Session 快取（TTL 30 分鐘）
cache_key = f"session:{user_id}"
await redis.set(cache_key, session_data, ex=1800)
```

**前端快取**:

- React Query: 自動快取與重新驗證
- Service Worker: 靜態資源快取

### 9.2 Database Optimization (資料庫優化)

**索引策略**:

- 所有外鍵建立索引
- 查詢頻繁的欄位建立索引
- 組合索引：`(stock_code, recorded_at)`

**查詢優化**:

- 避免 N+1 查詢（使用 `join` 或 `prefetch`）
- 分頁查詢（limit/offset）
- 使用 `EXPLAIN ANALYZE` 分析查詢計畫

### 9.3 API Rate Limiting (API 限流)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/v1/stocks")
@limiter.limit("60/minute")
async def list_stocks():
    pass
```

---

## 10. Error Handling (錯誤處理)

詳細規格參考：`docs/ERROR_HANDLING.md`

### 10.1 Exception Hierarchy (異常階層)

```python
class AuraTradeException(Exception):
    """基礎異常"""
    pass

class AuthenticationError(AuraTradeException):
    """認證錯誤 - HTTP 401"""
    pass

class AuthorizationError(AuraTradeException):
    """授權錯誤 - HTTP 403"""
    pass

class ResourceNotFoundError(AuraTradeException):
    """資源不存在 - HTTP 404"""
    pass

class BusinessLogicError(AuraTradeException):
    """業務邏輯錯誤 - HTTP 400"""
    pass
```

### 10.2 Error Logging (錯誤日誌)

```python
import logging
import json

logger = logging.getLogger(__name__)

@app.exception_handler(AuraTradeException)
async def handle_exception(request: Request, exc: AuraTradeException):
    logger.error(
        json.dumps({
            "error_code": exc.code,
            "message": exc.message,
            "trace_id": exc.trace_id,
            "path": request.url.path,
            "user_id": getattr(request.state, "user_id", None)
        })
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {...}}
    )
```

---

## 11. Testing Strategy (測試策略)

### 11.1 Unit Testing (單元測試)

**目標覆蓋率**: > 70%

**範例**:

```python
# tests/unit/services/test_stock_service.py
import pytest
from apps.services.stock_service import StockService

@pytest.mark.asyncio
async def test_get_stock_price_valid_code_returns_price():
    """測試：取得股價 - 有效股票代碼 - 返回價格"""
    # Arrange
    stock_service = StockService(mock_repo, mock_cache)
    stock_code = "2330"
    
    # Act
    result = await stock_service.get_real_time_price(stock_code)
    
    # Assert
    assert result.stock_code == "2330"
    assert result.price > 0
```

### 11.2 Integration Testing (整合測試)

```python
# tests/integration/api/test_stocks_api.py
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_stock_price_api():
    """測試：股價 API - 整合測試"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/stocks/2330/price")
        assert response.status_code == 200
        assert "price" in response.json()["data"]
```

### 11.3 E2E Testing (端對端測試)

**工具**: Playwright

```typescript
// frontend/tests/e2e/stock-monitoring.spec.ts
test('用戶可以新增股票至關注清單', async ({ page }) => {
  await page.goto('http://localhost:5173');
  await page.fill('#stock-search', '2330');
  await page.click('button:has-text("新增")');
  await expect(page.locator('.stock-card:has-text("2330")')).toBeVisible();
});
```

---

## 12. Deployment Architecture (部署架構)

### 12.1 Docker Configuration (Docker 配置)

**Dockerfile (Backend)**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Docker Compose**:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: auratrade
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 12.2 CI/CD Pipeline (CI/CD 流程)

```yaml
# .github/workflows/ci.yml
name: CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest
      
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # 部署腳本
```

---

## 13. Appendices (附錄)

### 13.1 Technology Stack Summary (技術棧總結)

| 類別 | 技術 | 版本 |
|------|------|------|
| 前端框架 | React | 18+ |
| 前端語言 | TypeScript | 5+ |
| 前端打包 | Vite | 4+ |
| 狀態管理 | Zustand / Redux Toolkit | - |
| HTTP 客戶端 | Axios | 1+ |
| 圖表庫 | Recharts | 2+ |
| 後端框架 | FastAPI | 0.100+ |
| 後端語言 | Python | 3.11+ |
| ORM | SQLAlchemy | 2.0+ |
| 資料庫 | PostgreSQL | 15+ |
| 快取 | Redis | 7+ |
| 認證 | JWT (python-jose) | - |
| 測試 (後端) | Pytest | 7+ |
| 測試 (前端) | Jest, Playwright | - |

### 13.2 Glossary (術語表)

參考 `docs/PRD.md` Section 12.1

---

**文檔結束**

**維護者**: AuraTrade Architecture Team  
**最後更新**: 2026-01-29  
**狀態**: ✅ 已審查並核准
