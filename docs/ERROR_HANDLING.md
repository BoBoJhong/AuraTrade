# AuraTrade 錯誤處理規範

## 🎯 目的

本文檔定義 AuraTrade 專案的統一錯誤處理標準，確保錯誤訊息的一致性、可讀性與可追溯性。

---

## 📊 統一錯誤碼表

### 錯誤碼格式

```
[模組代碼][錯誤類型][序號]

範例: AUTH_401_001
- AUTH: 認證模組
- 401: HTTP 狀態碼
- 001: 序號
```

### 完整錯誤碼表

#### 認證相關 (AUTH_)

| 錯誤碼 | HTTP | 說明 | 中文訊息 |
|--------|------|------|----------|
| AUTH_401_001 | 401 | Token 無效 | Token 無效或已過期 |
| AUTH_401_002 | 401 | Token 已過期 | Token 已過期，請重新登入 |
| AUTH_403_001 | 403 | 權限不足 | 您沒有權限執行此操作 |
| AUTH_400_001 | 400 | 密碼格式錯誤 | 密碼需至少 8 字元且包含英文與數字 |
| AUTH_409_001 | 409 | Email 已存在 | 此 Email 已被註冊 |
| AUTH_404_001 | 404 | 用戶不存在 | 找不到此用戶 |

#### 股票相關 (STOCK_)

| 錯誤碼 | HTTP | 說明 | 中文訊息 |
|--------|------|------|----------|
| STOCK_404_001 | 404 | 股票不存在 | 找不到股票代碼 {code} |
| STOCK_400_001 | 400 | 股票代碼格式錯誤 | 股票代碼格式不正確 |
| STOCK_503_001 | 503 | 數據源不可用 | 股價數據服務暫時不可用 |

#### 關注清單相關 (WATCHLIST_)

| 錯誤碼 | HTTP | 說明 | 中文訊息 |
|--------|------|------|----------|
| WATCHLIST_400_001 | 400 | 清單已滿 | 關注清單最多 50 支股票 |
| WATCHLIST_409_001 | 409 | 股票已存在 | 此股票已在關注清單中 |

#### AI 分析相關 (AI_)

| 錯誤碼 | HTTP | 說明 | 中文訊息 |
|--------|------|------|----------|
| AI_500_001 | 500 | AI 服務異常 | AI 分析服務異常，請稍後再試 |
| AI_429_001 | 429 | 請求過於頻繁 | AI 分析請求過於頻繁，請稍後再試 |

#### 系統相關 (SYS_)

| 錯誤碼 | HTTP | 說明 | 中文訊息 |
|--------|------|------|----------|
| SYS_500_001 | 500 | 內部伺服器錯誤 | 系統發生錯誤，請聯絡管理員 |
| SYS_503_001 | 503 | 服務暫時不可用 | 服務暫時維護中 |
| SYS_429_001 | 429 | 請求超過限制 | 請求過於頻繁，請稍後再試 |

---

## 📝 錯誤訊息格式

### API 錯誤回應標準格式

```json
{
  "error": {
    "code": "STOCK_404_001",
    "message": "找不到股票代碼 2330",
    "details": {
      "stock_code": "2330",
      "timestamp": "2026-01-29T10:30:00Z"
    },
    "trace_id": "uuid-1234-5678",
    "path": "/api/v1/stocks/2330"
  }
}
```

### 欄位說明

- `code`: 錯誤碼（必填）
- `message`: 用戶友善的錯誤訊息（必填）
- `details`: 額外的錯誤詳情（可選）
- `trace_id`: 追蹤 ID，用於日誌查詢（必填）
- `path`: 發生錯誤的 API 路徑（必填）

---

## 🔧 後端實作

### 自定義異常類

```python
# apps/core/exceptions.py
from fastapi import HTTPException
from typing import Optional, Dict, Any
import uuid

class AuraTradeException(Exception):
    """基礎異常類"""
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.trace_id = str(uuid.uuid4())
        super().__init__(message)

# 認證相關異常
class AuthenticationError(AuraTradeException):
    """認證錯誤"""
    def __init__(self, code: str, message: str):
        super().__init__(code, message, status_code=401)

class AuthorizationError(AuraTradeException):
    """授權錯誤"""
    def __init__(self, code: str, message: str):
        super().__init__(code, message, status_code=403)

# 資源相關異常
class ResourceNotFoundError(AuraTradeException):
    """資源不存在"""
    def __init__(self, code: str, message: str):
        super().__init__(code, message, status_code=404)

class ResourceConflictError(AuraTradeException):
    """資源衝突"""
    def __init__(self, code: str, message: str):
        super().__init__(code, message, status_code=409)

# 業務邏輯異常
class BusinessLogicError(AuraTradeException):
    """業務邏輯錯誤"""
    def __init__(self, code: str, message: str):
        super().__init__(code, message, status_code=400)

# 外部服務異常
class ExternalServiceError(AuraTradeException):
    """外部服務錯誤"""
    def __init__(self, code: str, message: str):
        super().__init__(code, message, status_code=503)
```

### 全域異常處理器

```python
# apps/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from apps.core.exceptions import AuraTradeException
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

@app.exception_handler(AuraTradeException)
async def auratrade_exception_handler(request: Request, exc: AuraTradeException):
    """處理自定義異常"""
    # 記錄錯誤日誌
    logger.error(
        f"Error {exc.code}: {exc.message}",
        extra={
            "trace_id": exc.trace_id,
            "path": request.url.path,
            "details": exc.details
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "trace_id": exc.trace_id,
                "path": str(request.url.path)
            }
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """處理未預期的異常"""
    trace_id = str(uuid.uuid4())
    
    # 記錄詳細錯誤
    logger.exception(
        f"Unhandled exception: {str(exc)}",
        extra={"trace_id": trace_id, "path": request.url.path}
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "SYS_500_001",
                "message": "系統發生錯誤，請聯絡管理員",
                "trace_id": trace_id,
                "path": str(request.url.path)
            }
        }
    )
```

### Service 層使用範例

```python
# apps/services/stock_service.py
from apps.core.exceptions import ResourceNotFoundError, ExternalServiceError

class StockService:
    async def get_stock_price(self, stock_code: str):
        # 查找股票
        stock = await self.stock_repo.find_by_code(stock_code)
        if not stock:
            raise ResourceNotFoundError(
                code="STOCK_404_001",
                message=f"找不到股票代碼 {stock_code}"
            )
        
        # 取得即時價格
        try:
            price = await self.external_api.get_price(stock_code)
        except Exception as e:
            raise ExternalServiceError(
                code="STOCK_503_001",
                message="股價數據服務暫時不可用"
            )
        
        return price
```

---

## 🎨 前端實作

### API 錯誤處理

```typescript
// src/services/api.ts
import axios, { AxiosError } from 'axios';

interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
    trace_id: string;
    path: string;
  };
}

// 全域錯誤處理
axios.interceptors.response.use(
  response => response,
  (error: AxiosError<ErrorResponse>) => {
    if (error.response?.data?.error) {
      const { code, message, trace_id } = error.response.data.error;
      
      // 記錄錯誤到日誌服務
      console.error(`[${trace_id}] ${code}: ${message}`);
      
      // 根據錯誤碼處理
      switch (code) {
        case 'AUTH_401_001':
        case 'AUTH_401_002':
          // Token 無效，導向登入頁
          window.location.href = '/login';
          break;
        
        case 'AUTH_403_001':
          // 權限不足
          toast.error('您沒有權限執行此操作');
          break;
        
        default:
          // 顯示錯誤訊息
          toast.error(message);
      }
    }
    
    return Promise.reject(error);
  }
);
```

### 錯誤提示元件

```typescript
// src/components/ErrorMessage.tsx
interface ErrorMessageProps {
  code?: string;
  message: string;
  details?: Record<string, any>;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ 
  code, 
  message, 
  details 
}) => {
  return (
    <div className="error-message">
      <div className="error-icon">⚠️</div>
      <div className="error-content">
        <h4>{message}</h4>
        {code && <span className="error-code">錯誤碼: {code}</span>}
        {details && process.env.NODE_ENV === 'development' && (
          <pre>{JSON.stringify(details, null, 2)}</pre>
        )}
      </div>
    </div>
  );
};
```

### React Error Boundary

```typescript
// src/components/ErrorBoundary.tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // 記錄到錯誤追蹤服務（如 Sentry）
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h1>發生錯誤</h1>
          <p>系統發生未預期的錯誤，請重新整理頁面</p>
          <button onClick={() => window.location.reload()}>
            重新整理
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

---

## 📋 錯誤日誌記錄

### 日誌格式

```python
# apps/utils/logger.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """結構化 JSON 日誌格式"""
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 添加額外欄位
        if hasattr(record, 'trace_id'):
            log_data['trace_id'] = record.trace_id
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'details'):
            log_data['details'] = record.details
        
        return json.dumps(log_data, ensure_ascii=False)

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/error.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.setFormatter(JSONFormatter())
```

### 日誌等級使用規範

| 等級 | 使用時機 | 範例 |
|------|---------|------|
| DEBUG | 開發調試訊息 | 「查詢 SQL: SELECT * FROM stocks」 |
| INFO | 一般資訊記錄 | 「用戶登入成功: user_id=123」 |
| WARNING | 警告但不影響運作 | 「快取未命中，從資料庫查詢」 |
| ERROR | 錯誤但可恢復 | 「股價 API 調用失敗，使用快取數據」 |
| CRITICAL | 嚴重錯誤需立即處理 | 「資料庫連線中斷」 |

---

## ✅ 錯誤處理檢查清單

### 開發階段

- [ ] 所有可預期的錯誤都有對應的錯誤碼
- [ ] 錯誤訊息清晰且用戶友善
- [ ] 敏感資訊不出現在錯誤訊息中
- [ ] 錯誤日誌包含 trace_id 便於追蹤

### 測試階段

- [ ] 測試所有錯誤情境
- [ ] 驗證錯誤回應格式正確
- [ ] 確認前端正確顯示錯誤訊息
- [ ] 檢查錯誤日誌完整記錄

### 生產環境

- [ ] 錯誤日誌正確寫入
- [ ] 嚴重錯誤有告警機制
- [ ] 定期檢查錯誤日誌
- [ ] 根據錯誤頻率優化系統

---

## 📚 相關文檔

- [安全規範](./SECURITY.md)
- [監控規範](./MONITORING.md)
- [API 文檔](./API.md)

---

**最後更新**: 2026-01-29  
**版本**: 1.0  
**維護者**: AuraTrade Development Team
