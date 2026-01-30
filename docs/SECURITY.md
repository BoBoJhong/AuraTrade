# AuraTrade 安全規範

## 🔒 安全原則

本文檔定義 AuraTrade 專案的安全標準與最佳實踐，確保系統安全性與用戶資料保護。

---

## 🔐 認證機制 (Authentication)

### JWT (JSON Web Token) 實作標準

#### Token 結構

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "uuid",
    "email": "user@example.com",
    "role": "user",
    "exp": 1234567890,
    "iat": 1234567890
  }
}
```

#### Token 生成規範

**後端實作** (Python/FastAPI):

```python
# apps/core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# 配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # 至少 32 字元
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict) -> str:
    """生成 Access Token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """生成 Refresh Token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    """驗證 Token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="無效的 Token")
```

#### Token 儲存規範

**前端實作** (React):

```typescript
// src/services/authService.ts
class AuthService {
  // 儲存 Token 到 HttpOnly Cookie（最安全）
  setTokens(accessToken: string, refreshToken: string) {
    // 由後端設置 HttpOnly Cookie
    // 前端無法透過 JavaScript 存取（防止 XSS）
  }
  
  // 或使用 Memory Storage（次選）
  private accessToken: string | null = null;
  
  setAccessToken(token: string) {
    this.accessToken = token; // 僅存於記憶體
  }
  
  // ❌ 不要使用 localStorage（容易受 XSS 攻擊）
  // ❌ 不要使用 sessionStorage（容易受 XSS 攻擊）
}
```

#### Token 刷新機制

```typescript
// src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  withCredentials: true  // 發送 Cookie
});

// 401 錯誤時自動刷新 Token
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      try {
        // 使用 Refresh Token 取得新的 Access Token
        await api.post('/auth/refresh');
        // 重試原請求
        return api.request(error.config);
      } catch (refreshError) {
        // Refresh 失敗，導向登入頁
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
```

---

## 🛡️ 授權機制 (Authorization)

### RBAC (Role-Based Access Control)

#### 角色定義

```python
# apps/models/user.py
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"          # 系統管理員
    USER = "user"            # 一般用戶
    READONLY = "readonly"    # 唯讀用戶（未來擴展）
```

#### 權限檢查裝飾器

```python
# apps/core/security.py
from fastapi import Depends, HTTPException
from apps.models.user import UserRole

def require_role(*allowed_roles: UserRole):
    """檢查用戶角色的依賴注入"""
    async def role_checker(
        current_user = Depends(get_current_user)
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="權限不足"
            )
        return current_user
    return role_checker

# 使用範例
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user = Depends(require_role(UserRole.ADMIN))
):
    # 只有 admin 可以刪除用戶
    pass
```

---

## 🔑 密碼安全

### 密碼複雜度要求

- ✅ 最少 8 字元
- ✅ 包含英文字母（大小寫）
- ✅ 包含數字
- ✅ 建議包含特殊符號

### 密碼加密

```python
# apps/core/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """使用 bcrypt 加密密碼（10 輪加鹽）"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證密碼"""
    return pwd_context.verify(plain_password, hashed_password)
```

### 密碼驗證

```python
# apps/api/v1/schemas/auth.py
from pydantic import BaseModel, validator
import re

class UserRegistration(BaseModel):
    email: str
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密碼至少需要 8 個字元')
        if not re.search(r'[a-z]', v):
            raise ValueError('密碼需包含小寫字母')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密碼需包含大寫字母')
        if not re.search(r'\d', v):
            raise ValueError('密碼需包含數字')
        return v
```

---

## 🌐 CORS 配置

### 開發環境

```python
# apps/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)
```

### 生產環境

```python
# apps/main.py
import os

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # 來自環境變數
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=600,  # Preflight 快取 10 分鐘
)
```

---

## 🚦 Rate Limiting

### API 限流策略

#### 全域限流

```python
# apps/middleware/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# 全域限制：每分鐘 60 次請求
@app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

#### 端點級別限流

```python
from slowapi import Limiter

@router.post("/auth/login")
@limiter.limit("5/minute")  # 登入限制：每分鐘 5 次
async def login(request: Request, credentials: LoginSchema):
    pass

@router.post("/api/v1/stocks/search")
@limiter.limit("30/minute")  # 搜尋限制：每分鐘 30 次
async def search_stocks(request: Request):
    pass
```

---

## 🛡️ 防護措施

### SQL Injection 防護

✅ **正確做法** - 使用 ORM 參數化查詢:

```python
# apps/repositories/stock_repository.py
from sqlalchemy import select

async def find_by_code(self, code: str) -> Optional[Stock]:
    # ✅ SQLAlchemy 自動防止 SQL Injection
    result = await self.db.execute(
        select(Stock).where(Stock.code == code)
    )
    return result.scalar_one_or_none()
```

❌ **錯誤做法** - 字串拼接:

```python
# ❌ 永遠不要這樣做
query = f"SELECT * FROM stocks WHERE code = '{code}'"
```

### XSS (Cross-Site Scripting) 防護

#### 後端輸出編碼

```python
# apps/api/v1/schemas/stock.py
from pydantic import BaseModel, validator
import html

class StockResponse(BaseModel):
    code: str
    name: str
    
    @validator('name')
    def sanitize_name(cls, v):
        # HTML 編碼，防止 XSS
        return html.escape(v)
```

#### 前端防護

```typescript
// src/components/StockCard.tsx
import DOMPurify from 'dompurify';

function StockCard({ stock }) {
  // ✅ 使用 React 的自動轉義
  return <div>{stock.name}</div>;
  
  // 如需渲染 HTML，使用 DOMPurify
  const cleanHTML = DOMPurify.sanitize(stock.description);
  return <div dangerouslySetInnerHTML={{ __html: cleanHTML }} />;
}
```

### CSRF (Cross-Site Request Forgery) 防護

```python
# apps/middleware/csrf.py
from fastapi_csrf_protect import CsrfProtect

@app.post("/api/v1/sensitive-action")
async def sensitive_action(csrf_protect: CsrfProtect = Depends()):
    await csrf_protect.validate_csrf()
    # 執行敏感操作
```

---

## 🔐 敏感資料處理

### 環境變數管理

```bash
# .env (不要提交到 Git)
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
DATABASE_PASSWORD=your-database-password
GEMINI_API_KEY=your-gemini-api-key
LINE_CHANNEL_SECRET=your-line-secret

# ✅ 使用環境變數
# ❌ 不要硬編碼在代碼中
```

### 敏感欄位加密

```python
# apps/models/user.py
from cryptography.fernet import Fernet
import os

cipher = Fernet(os.getenv("ENCRYPTION_KEY").encode())

class User(Base):
    __tablename__ = "users"
    
    _phone = Column("phone", String(255))  # 加密儲存
    
    @property
    def phone(self):
        """解密電話號碼"""
        if self._phone:
            return cipher.decrypt(self._phone.encode()).decode()
        return None
    
    @phone.setter
    def phone(self, value):
        """加密電話號碼"""
        if value:
            self._phone = cipher.encrypt(value.encode()).decode()
```

### 日誌脫敏

```python
# apps/utils/logger.py
import logging
import re

class SensitiveDataFilter(logging.Filter):
    """過濾敏感資料"""
    SENSITIVE_PATTERNS = [
        (r'"password"\s*:\s*"[^"]*"', '"password": "***"'),
        (r'"token"\s*:\s*"[^"]*"', '"token": "***"'),
        (r'\b\d{16}\b', '****-****-****-****'),  # 信用卡號
    ]
    
    def filter(self, record):
        message = record.getMessage()
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            message = re.sub(pattern, replacement, message)
        record.msg = message
        return True
```

---

## 🔒 HTTPS 強制

### 生產環境強制 HTTPS

```python
# apps/middleware/https.py
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

### HSTS Header

```python
# apps/middleware/security_headers.py
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response
```

---

## ✅ 安全檢查清單

### 開發階段

- [ ] 所有密碼使用 bcrypt 加密
- [ ] 所有 API 端點有適當的認證保護
- [ ] 敏感資料不出現在日誌中
- [ ] 使用 ORM 防止 SQL Injection
- [ ] 前端輸出經過轉義防止 XSS
- [ ] 環境變數不硬編碼在代碼中

### 部署前

- [ ] HTTPS 已啟用
- [ ] CORS 配置正確（生產域名）
- [ ] Rate Limiting 已設置
- [ ] 安全 Headers 已配置
- [ ] JWT Secret 至少 32 字元且足夠隨機
- [ ] 資料庫密碼夠強（至少 16 字元）

### 定期審查

- [ ] 每月檢查依賴套件漏洞（`npm audit`, `safety check`）
- [ ] 每季度進行滲透測試
- [ ] 每半年更新 JWT Secret
- [ ] 監控異常登入嘗試

---

## 📚 相關文檔

- [錯誤處理規範](./ERROR_HANDLING.md)
- [環境配置指南](./ENVIRONMENT_SETUP.md)
- [API 文檔](./API.md)
- [SDD - 安全設計](./SDD.md#security-design)

---

## 🔗 參考資源

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

**最後更新**: 2026-01-29  
**版本**: 1.0  
**維護者**: AuraTrade Security Team
