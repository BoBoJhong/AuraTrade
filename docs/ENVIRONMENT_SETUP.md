# AuraTrade 環境設置指南

## 🎯 目的

本文檔說明如何設置 AuraTrade 開發環境，包含前端、後端、資料庫與第三方服務配置。

---

## 📋 系統需求

### 硬體需求

- **CPU**: 4 核心以上
- **記憶體**: 8GB RAM 以上（建議 16GB）
- **硬碟**: 20GB 可用空間

### 作業系統

- **Windows**: 10/11（支援 WSL2）
- **macOS**: 10.15 以上
- **Linux**: Ubuntu 20.04+ / Debian 11+

---

## 🛠️ 基礎環境安裝

### 1. Node.js (前端)

**版本要求**: v18.0.0 以上（建議 v20 LTS）

#### 安裝方式

**使用 nvm（推薦）**:

```bash
# 安裝 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 安裝 Node.js
nvm install 20
nvm use 20
nvm alias default 20

# 驗證安裝
node --version  # 應顯示 v20.x.x
npm --version   # 應顯示 10.x.x
```

**或直接下載**:

- 官方網站: <https://nodejs.org/>

### 2. Python (後端)

**版本要求**: v3.10 以上（建議 v3.11）

#### 安裝方式

**macOS/Linux**:

```bash
# 使用 pyenv（推薦）
curl https://pyenv.run | bash

# 安裝 Python
pyenv install 3.11.0
pyenv global 3.11.0

# 驗證安裝
python --version  # 應顯示 Python 3.11.0
```

**Windows**:

- 官方網站: <https://www.python.org/downloads/>

#### 設置虛擬環境

```bash
# 進入後端目錄
cd backend

# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

### 3. PostgreSQL (資料庫)

**版本要求**: v14 以上（建議 v15）

#### 使用 Docker（推薦）

```bash
# 建立 PostgreSQL 容器
docker run --name auratrade-db \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=auratrade \
  -p 5432:5432 \
  -d postgres:15

# 驗證運行
docker ps | grep auratrade-db
```

#### 本地安裝

- **macOS**: `brew install postgresql@15`
- **Ubuntu**: `sudo apt install postgresql-15`
- **Windows**: <https://www.postgresql.org/download/windows/>

---

## ⚙️ 環境變數配置

### 1. 複製環境變數範例

```bash
# 專案根目錄
cp .env.example .env

# 前端
cp frontend/.env.example frontend/.env

# 後端
cp backend/.env.example backend/.env
```

### 2. 配置根目錄 .env

```bash
# .env
# 環境
ENVIRONMENT=development  # development / staging / production

# 資料庫
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/auratrade

# Redis（可選）
REDIS_URL=redis://localhost:6379/0
```

### 3. 配置後端 .env

```bash
# backend/.env

# 應用設定
APP_NAME=AuraTrade
APP_VERSION=1.0.0
DEBUG=True

# 資料庫
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/auratrade

# JWT 安全
JWT_SECRET_KEY=your-super-secret-key-min-32-characters-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Google Gemini API
GEMINI_API_KEY=your-gemini-api-key

# LINE Messaging API
LINE_CHANNEL_ACCESS_TOKEN=your-line-token
LINE_CHANNEL_SECRET=your-line-secret

# 股價 API（依使用的服務）
STOCK_API_KEY=your-stock-api-key
STOCK_API_URL=https://api.stock-service.com

# 日誌
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### 4. 配置前端 .env

```bash
# frontend/.env

# API Base URL
VITE_API_BASE_URL=http://localhost:8000/api/v1

# WebSocket URL
VITE_WS_URL=ws://localhost:8000/ws

# 環境
VITE_ENVIRONMENT=development

# Google Analytics（生產環境）
# VITE_GA_TRACKING_ID=UA-XXXXX-X
```

---

## 📦 依賴安裝

### 前端依賴

```bash
cd frontend

# 安裝 npm 套件
npm install

# 或使用 pnpm（更快）
pnpm install

# 安裝完成後驗證
npm list
```

### 後端依賴

```bash
cd backend

# 啟動虛擬環境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安裝 Python套件
pip install -r requirements.txt

# 開發工具（可選）
pip install -r requirements-dev.txt

# 驗證安裝
pip list
```

---

## 🗄️ 資料庫設置

### 1. 建立資料庫

```bash
# 使用 psql
psql -U postgres

# 建立資料庫
CREATE DATABASE auratrade;

# 建立用戶（可選）
CREATE USER auratrade_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE auratrade TO auratrade_user;

# 結束
\q
```

### 2. 執行資料庫遷移

```bash
cd backend

# 使用 Alembic
alembic upgrade head

# 或使用自定義遷移腳本
python scripts/migrate.py
```

### 3. 填充測試數據（可選）

```bash
# 執行 seed script
python scripts/seed_data.py
```

---

## 🐳 Docker 設置（可選）

### 使用 Docker Compose

```bash
# 啟動所有服務
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f

# 停止服務
docker-compose down
```

### docker-compose.yml 說明

```yaml
version: '3.8'

services:
  # PostgreSQL 資料庫
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: auratrade
      POSTGRES_PASSWORD: your_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Redis (可選)
  redis:
    image: redis:7
    ports:
      - "6379:6379"

  # 後端 API
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    env_file:
      - ./backend/.env

  # 前端
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    env_file:
      - ./frontend/.env

volumes:
  postgres_data:
```

---

## 🚀 啟動專案

### 開發模式

#### 1. 啟動後端

```bash
cd backend

# 啟動 FastAPI
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或使用 python
python main.py

# 驗證: 訪問 http://localhost:8000/docs
```

#### 2. 啟動前端

```bash
cd frontend

# 啟動 Vite dev server
npm run dev

# 驗證: 訪問 http://localhost:5173
```

#### 3. 啟動背景任務（可選）

```bash
cd backend

# 啟動爬蟲排程
python -m apps.tasks.schedulers.news_scheduler

# 或使用 Celery（如有配置）
celery -A apps.tasks worker --loglevel=info
```

### 生產模式

#### 後端

```bash
# 使用 Gunicorn + Uvicorn workers
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

#### 前端

```bash
# 建立生產版本
npm run build

# 使用 nginx 或其他 web server 提供靜態檔案
npx serve -s dist -p 3000
```

---

## 🧪 驗證設置

### 檢查清單

- [ ] Node.js 版本 ≥ v18
- [ ] Python 版本 ≥ v3.10
- [ ] PostgreSQL 運行中
- [ ] 環境變數已配置
- [ ] 資料庫遷移成功
- [ ] 後端 API 可訪問 (<http://localhost:8000/docs>)
- [ ] 前端應用可訪問 (<http://localhost:5173>)

### 執行測試

```bash
# 後端測試
cd backend
pytest

# 前端測試
cd frontend
npm test

# E2E 測試
npm run test:e2e
```

---

## 🔧 IDE 配置

### VS Code（推薦）

#### 安裝擴展

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "ms-azuretools.vscode-docker"
  ]
}
```

#### 設定檔

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/bin/python",
 "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
"editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

---

## 🐛 常見問題

### Q1: PostgreSQL 連線失敗

```bash
# 檢查 PostgreSQL 是否運行
brew services list  # macOS
sudo systemctl status postgresql  # Linux

# 檢查連線參數
pg_isready -h localhost -p 5432
```

### Q2: npm install 失敗

```bash
# 清除快取
npm cache clean --force

# 刪除 node_modules
rm -rf node_modules package-lock.json

# 重新安裝
npm install
```

### Q3: Python 套件安裝失敗

```bash
# 升級 pip
pip install --upgrade pip

# 使用國內鏡像（中國地區）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q4: Port 已被佔用

```bash
# 查找佔用 port 的程序
# macOS/Linux
lsof -i :8000
# Windows
netstat -ano | findstr :8000

# 終止程序
kill -9 <PID>
```

---

## 📚 相關文檔

- [開發規範](../.antigravity/rules.md)
- [安全規範](./SECURITY.md)
- [部署指南](./DEPLOYMENT.md)

---

**最後更新**: 2026-01-29  
**版本**: 1.0  
**維護者**: AuraTrade Development Team
