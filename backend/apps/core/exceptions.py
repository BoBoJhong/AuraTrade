"""
Custom Exceptions
追溯: REQ-095, docs/ERROR_HANDLING.md
"""
from typing import Optional


class AuraTradeException(Exception):
    """Base exception for AuraTrade"""
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 500,
        trace_id: Optional[str] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.trace_id = trace_id
        super().__init__(self.message)


class AuthenticationError(AuraTradeException):
    """Authentication failed - HTTP 401"""
    def __init__(self, message: str = "認證失敗", code: str = "AUTH_401_001", trace_id: Optional[str] = None):
        super().__init__(message, code, 401, trace_id)


class AuthorizationError(AuraTradeException):
    """Authorization failed - HTTP 403"""
    def __init__(self, message: str = "權限不足", code: str = "AUTH_403_001", trace_id: Optional[str] = None):
        super().__init__(message, code, 403, trace_id)


class ResourceNotFoundError(AuraTradeException):
    """Resource not found - HTTP 404"""
    def __init__(self, message: str = "資源不存在", code: str = "SYS_404_001", trace_id: Optional[str] = None):
        super().__init__(message, code, 404, trace_id)


class StockNotFoundError(ResourceNotFoundError):
    """Stock not found"""
    def __init__(self, stock_code: str, trace_id: Optional[str] = None):
        super().__init__(
            message=f"找不到股票代碼: {stock_code}",
            code="STOCK_404_001",
            trace_id=trace_id
        )


class BusinessLogicError(AuraTradeException):
    """Business logic error - HTTP 400"""
    def __init__(self, message: str, code: str = "SYS_400_001", trace_id: Optional[str] = None):
        super().__init__(message, code, 400, trace_id)


class WatchlistLimitExceededError(BusinessLogicError):
    """Watchlist limit exceeded - BR-01"""
    def __init__(self, limit: int = 50, trace_id: Optional[str] = None):
        super().__init__(
            message=f"關注清單已達上限（{limit} 支股票）",
            code="STOCK_400_001",
            trace_id=trace_id
        )


class DailyLimitExceededError(BusinessLogicError):
    """Daily request limit exceeded"""
    def __init__(self, service: str, limit: int, trace_id: Optional[str] = None):
        super().__init__(
            message=f"{service} 每日請求已達上限（{limit} 次），請明日再試",
            code="SYS_400_002",
            trace_id=trace_id
        )


class ExternalAPIError(AuraTradeException):
    """External API error - HTTP 503"""
    def __init__(self, service: str, message: str = "外部服務暫時無法使用", trace_id: Optional[str] = None):
        super().__init__(
            message=f"{service}: {message}",
            code="SYS_503_001",
            status_code=503,
            trace_id=trace_id
        )
