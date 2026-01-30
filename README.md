# AuraTrade - AI 驅動的智能投資分析系統

## 🚀 快速開始 (使用 Docker)

### 先決條件

- Docker Desktop 已安裝並運行
- Git

### 啟動專案

```bash
# 1. Clone 專案
git clone <repository-url>
cd AuraTrade

# 2. 複製環境變數範例
cp backend/.env.example backend/.env

# 3. 啟動所有服務
docker-compose up -d

# 4. 查看日誌
docker-compose logs -f

# 5. 停止服務
docker-compose down
```

### 服務端點

- **前端**: <http://localhost:5173>
- **後端 API**: <http://localhost:8000>
- **API 文檔**: <http://localhost:8000/api/docs>
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 📁 專案結構

```
AuraTrade/
├── backend/              # FastAPI 後端
│   ├── apps/
│   │   ├── api/          # API Layer
│   │   ├── services/     # Service Layer
│   │   ├── repositories/ # Repository Layer
│   │   ├── models/       # ORM Models
│   │   └── core/         # Core Configuration
│   ├── tests/            # 測試
│   ├── main.py           # 應用入口
│   └── requirements.txt
│
├── frontend/             # React 前端
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── stores/
│   └── package.json
│
├── docs/                 # 專案文檔
│   ├── PRD.md
│   ├── SRS.md
│   ├── SDD.md
│   └── diagrams/
│
└── docker-compose.yml
```

## 🛠️ 開發指南

### 後端開發

```bash
# 進入後端容器
docker-compose exec backend bash

# 運行測試
pytest

# 查看測試覆蓋率
pytest --cov=apps

# 代碼格式化
black apps/
flake8 apps/
```

### 前端開發

```bash
# 進入前端容器
docker-compose exec frontend sh

# 運行測試
npm test

# 代碼格式化
npm run lint
```

### 資料庫遷移

```bash
# 創建遷移
docker-compose exec backend alembic revision --autogenerate -m "description"

# 執行遷移
docker-compose exec backend alembic upgrade head

# 回滾遷移
docker-compose exec backend alembic downgrade -1
```

## 📚 文檔

- [產品需求文檔 (PRD)](./docs/PRD.md)
- [軟體需求規格書 (SRS)](./docs/SRS.md)
- [軟體設計文檔 (SDD)](./docs/SDD.md)
- [API 文檔](./docs/API.md)
- [資料庫 Schema](./docs/DB_SCHEMA.md)
- [安全規範](./docs/SECURITY.md)
- [錯誤處理](./docs/ERROR_HANDLING.md)
- [環境設置](./docs/ENVIRONMENT_SETUP.md)

## 🧪 測試

```bash
# 後端測試
docker-compose exec backend pytest

# 前端測試
docker-compose exec frontend npm test

# E2E 測試
docker-compose exec frontend npm run test:e2e
```

## 📦 部署

參考 [部署指南](./docs/DEPLOYMENT.md)

## 🤝 貢獻

參考 [貢獻指南](./.github/CONTRIBUTING.md)

## 📄 授權

私有專案 - 保留所有權利

## 👥 團隊

- 開發團隊: AuraTrade Development Team

---

**最後更新**: 2026-01-29  
**版本**: 1.0.0
