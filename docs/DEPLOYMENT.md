# AuraTrade 部署指南

## 🎯 部署策略

採用**藍綠部署**策略，確保零停機時間。

## 🚀 部署流程

### 1. 部署前檢查

- [ ] 所有測試通過（單元/整合/E2E）
- [ ] 代碼審查完成
- [ ] 文檔已更新
- [ ] 資料庫遷移腳本已準備

### 2. Staging 部署

```bash
# 部署到預發環境
git checkout main
git pull origin main
docker-compose -f docker-compose.staging.yml up -d

# 執行煙霧測試
npm run test:smoke
```

### 3. Production 部署

```bash
# 藍綠部署腳本
./scripts/deployment/blue-green-deploy.sh

# 或使用 CI/CD
# GitHub Actions 會自動部署
```

### 4. 部署後驗證

- [ ] 健康檢查通過 (GET /health)
- [ ] 關鍵 API 響應正常
- [ ] 監控指標正常
- [ ] 日誌無錯誤

## 🔄 回滾策略

如發現問題，立即回滾：

```bash
# 快速回滾到前一版本
./scripts/deployment/rollback.sh

# 或手動切換到藍色環境
docker-compose -f docker-compose.blue.yml up -d
```

## 🐳 Docker 部署

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    image: auratrade/backend:latest
    environment:
      - ENVIRONMENT=production
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

## 📚 相關文檔

- [環境設置](./ENVIRONMENT_SETUP.md)
- [監控規範](./MONITORING.md)
