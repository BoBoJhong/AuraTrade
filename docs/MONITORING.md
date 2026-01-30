# AuraTrade 監控與日誌規範

## 🎯 目的

定義監控指標、日誌格式、告警規則，確保生產環境可觀測性。

## 📊 監控指標

### 系統層級指標

- **CPU 使用率**: 目標 < 70%，警告 > 80%
- **記憶體使用率**: 目標 < 75%，警告 > 85%
- **磁碟使用率**: 目標 < 80%，警告 > 90%

### 應用層級指標

- **API 響應時間**: P95 < 2s，P99 < 5s
- **錯誤率**: < 1%
- **QPS**: 監控每秒請求數
- **資料庫連線數**: 監控連線池使用率

### 業務層級指標

- **活躍用戶數**: 每日/每週/每月
- **股價更新延遲**: < 2 秒
- **AI 分析成功率**: > 95%

## 📝 結構化日誌格式

```json
{
  "timestamp": "2026-01-29T10:30:00.123Z",
  "level": "INFO",
  "service": "auratrade-backend",
  "module": "stock_service",
  "function": "get_real_time_price",
  "message": "取得股價成功",
  "trace_id": "uuid-1234",
  "user_id": "user-5678",
  "stock_code": "2330",
  "duration_ms": 125,
  "status": "success"
}
```

## 🚨 告警規則

### Critical (P0) - 立即處理

- API 錯誤率 > 5%（5分鐘內）
- 資料庫連線失敗
- 服務宕機

### High (P1) - 1小時內處理

- API 響應時間 P95 > 5s
- 記憶體使用率 > 90%
- 錯誤率 > 2%

### Medium (P2) - 當天處理

- CPU 使用率 > 80%
- 磁碟使用率 > 85%

## 🛠️ 監控工具

**推薦棧**:

- **後端監控**: Prometheus + Grafana
- **日誌收集**: ELK Stack (Elasticsearch + Logstash + Kibana)
- **APM**: Sentry / New Relic
- **正常運行監控**: UptimeRobot

## 📚 相關文檔

- [錯誤處理規範](./ERROR_HANDLING.md)
- [部署指南](./DEPLOYMENT.md)
