# GitHub Actions Workflows

本目錄包含 AuraTrade 的 CI/CD 工作流程。

## Workflows

### 1) CI (`ci.yml`)

觸發時機：
- push 到 `main`、`develop`
- pull request 到 `main`、`develop`

執行內容：
- Backend: flake8 + pytest
- Frontend: lint + type-check + build
- Docker: backend/frontend image build 驗證

### 2) CD (`cd.yml`)

觸發時機：
- push 到 `main`
- push tag `v*`

執行內容：
- 建置並推送 Docker 映像到 Docker Hub
- 可選：若設定 SSH secrets，會執行遠端 `docker compose pull && docker compose up -d`

### 3) Manual Regression (`tests.yml`)

觸發時機：
- 手動執行（workflow_dispatch）

執行內容：
- Backend regression tests（含 unit/integration 路徑）
- Frontend lint/type-check/build

## Required Secrets

最少需要：
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`（建議用 Docker Hub Access Token）

選用：
- `FUGLE_API_KEY`
- `ALPHA_VANTAGE_API_KEY`
- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_SSH_KEY`
- `DEPLOY_PATH`

## 建議保護規則

- 保護 `main` 分支，要求 CI 綠燈才能 merge。
- PR 必須至少通過 `Backend Lint and Tests` 與 `Frontend Lint Typecheck Build`。