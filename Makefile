# AuraTrade Makefile
# 統一開發命令接口

.PHONY: help install test test-unit test-integration test-e2e sentinel-init sentinel-scan sentinel-full clean docs

# 預設目標
.DEFAULT_GOAL := help

help: ## 顯示幫助訊息
	@echo "AuraTrade 開發命令"
	@echo "===================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# === 環境設置 ===

install: ## 安裝所有依賴
	@echo "📦 安裝後端依賴..."
	cd backend && pip install -r requirements.txt
	cd backend && pip install -r requirements-test.txt
	@echo "📦 安裝前端依賴..."
	cd frontend && npm install
	@echo "✅ 依賴安裝完成"

install-backend: ## 安裝後端依賴
	cd backend && pip install -r requirements.txt
	cd backend && pip install -r requirements-test.txt

install-frontend: ## 安裝前端依賴
	cd frontend && npm install

# === 測試命令 ===

test: ## 執行所有測試
	@echo "🧪 執行所有測試..."
	@make test-unit
	@make test-integration

test-unit: ## 執行單元測試
	@echo "🧪 執行單元測試..."
	cd backend && python -m pytest ../tests/unit/ -v --tb=short

test-integration: ## 執行整合測試
	@echo "🧪 執行整合測試..."
	cd backend && python -m pytest ../tests/integration/ -v --tb=short

test-e2e: ## 執行 E2E 測試
	@echo "🧪 執行 E2E 測試..."
	cd frontend && npm run test:e2e

test-perf: ## 執行性能測試
	@echo "🚀 執行性能測試..."
	locust -f tests/performance/locustfile.py --host=http://localhost:8000 --users 50 --spawn-rate 5 --run-time 2m --headless

test-coverage: ## 測試覆蓋率報告
	@echo "📊 生成覆蓋率報告..."
	cd backend && python -m pytest ../tests/unit/ --cov=apps --cov-report=html --cov-report=term

# === Sentinel Agent 命令 ===

sentinel-init: ## 初始化 Sentinel Agent
	@echo "🛡️  初始化 Sentinel Agent..."
	python sentinel-cli.py init

sentinel-scan: ## 掃描專案
	@echo "🔍 掃描專案..."
	python sentinel-cli.py scan

sentinel-full: ## 執行完整測試週期 (Sentinel)
	@echo "🛡️  執行 Sentinel 完整測試週期..."
	python sentinel-cli.py full-cycle

sentinel-report: ## 產出測試報告
	@echo "📋 產出測試報告..."
	python sentinel-cli.py report

# === 開發服務器 ===

run-backend: ## 啟動後端服務器
	@echo "🚀 啟動後端服務器..."
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## 啟動前端服務器
	@echo "🚀 啟動前端服務器..."
	cd frontend && npm run dev

run: ## 啟動所有服務 (後端 + 前端)
	@echo "🚀 啟動所有服務..."
	@make -j2 run-backend run-frontend

# === 代碼品質 ===

lint: ## 執行 Linting
	@echo "🔍 執行 Linting..."
	cd backend && black . --check
	cd backend && flake8 .
	cd frontend && npm run lint

format: ## 格式化代碼
	@echo "✨ 格式化代碼..."
	cd backend && black .
	cd frontend && npm run format

# === 資料庫 ===

db-migrate: ## 執行資料庫遷移
	@echo "🗄️  執行資料庫遷移..."
	cd backend && alembic upgrade head

db-rollback: ## 回滾資料庫
	@echo "🗄️  回滾資料庫..."
	cd backend && alembic downgrade -1

db-reset: ## 重置資料庫
	@echo "🗄️  重置資料庫..."
	cd backend && alembic downgrade base
	cd backend && alembic upgrade head

# === Docker ===

docker-build: ## 構建 Docker 映像
	@echo "🐳 構建 Docker 映像..."
	docker-compose build

docker-up: ## 啟動 Docker 容器
	@echo "🐳 啟動 Docker 容器..."
	docker-compose up -d

docker-down: ## 停止 Docker 容器
	@echo "🐳 停止 Docker 容器..."
	docker-compose down

docker-logs: ## 查看 Docker 日誌
	docker-compose logs -f

# === 清理 ===

clean: ## 清理臨時文件
	@echo "🧹 清理臨時文件..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "node_modules" -exec rm -rf {} +
	@echo "✅ 清理完成"

clean-test: ## 清理測試緩存
	@echo "🧹 清理測試緩存..."
	rm -rf tests/.pytest_cache
	rm -rf tests/reports/.coverage
	rm -rf backend/htmlcov

# === 文檔 ===

docs: ## 生成文檔
	@echo "📚 生成文檔..."
	@echo "文檔位置: docs/"

docs-serve: ## 啟動文檔服務器
	@echo "📚 啟動文檔服務器..."
	cd docs && python -m http.server 8080

# === CI/CD ===

ci-test: ## CI 測試 (模擬)
	@echo "🔄 執行 CI 測試..."
	@make test-unit
	@make test-integration
	@make lint
	@make test-coverage

# === 快捷命令別名 ===

unit: test-unit ## (alias) 單元測試
integration: test-integration ## (alias) 整合測試
e2e: test-e2e ## (alias) E2E 測試
coverage: test-coverage ## (alias) 覆蓋率
perf: test-perf ## (alias) 性能測試

# Sentinel 簡寫
st-init: sentinel-init ## (alias) Sentinel 初始化
st-scan: sentinel-scan ## (alias) Sentinel 掃描
st-full: sentinel-full ## (alias) Sentinel 完整週期
st: sentinel-full ## (alias) Sentinel 完整週期 (最短)
