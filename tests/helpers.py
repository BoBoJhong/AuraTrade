"""
Test Helper Functions
測試輔助函數 - 提供驗證和斷言輔助

根據 IMPROVEMENTS.md Priority 4 實施
"""
from typing import Any, Dict, List
from httpx import Response


def assert_error_response(
    response: Response,
    expected_status: int,
    error_keywords: List[str]
):
    """
    驗證錯誤回應的輔助函數
    
    Args:
        response: HTTP 回應物件
        expected_status: 預期的 HTTP 狀態碼
        error_keywords: 應該出現在錯誤訊息中的關鍵字列表
        
    Raises:
        AssertionError: 如果驗證失敗
        
    Example:
        assert_error_response(
            response, 
            400, 
            ["email", "invalid"]
        )
    """
    assert response.status_code == expected_status, \
        f"Expected status {expected_status}, got {response.status_code}"
    
    try:
        error = response.json()
    except Exception:
        error = {"detail": response.text}
    
    error_str = str(error).lower()
    
    for keyword in error_keywords:
        assert keyword.lower() in error_str, \
            f"Expected keyword '{keyword}' in error message: {error}"


def assert_success_response(
    response: Response,
    expected_status: int = 200,
    required_fields: List[str] = None
):
    """
    驗證成功回應
    
    Args:
        response: HTTP 回應物件
        expected_status: 預期狀態碼，預設 200
        required_fields: 必須存在的欄位列表
    """
    assert response.status_code == expected_status, \
        f"Expected status {expected_status}, got {response.status_code}"
    
    if required_fields:
        data = response.json()
        for field in required_fields:
            assert field in data, \
                f"Required field '{field}' not found in response"


def assert_valid_pagination(data: Dict[str, Any]):
    """
    驗證分頁回應結構
    
    Args:
        data: 回應數據字典
    """
    assert "total" in data or "count" in data, \
        "Pagination response should have 'total' or 'count'"
    
    assert "data" in data or "results" in data or "items" in data, \
        "Pagination response should have data container"


def assert_valid_timestamp(timestamp_str: str):
    """
    驗證時間戳格式
    
    Args:
        timestamp_str: ISO 格式的時間戳字串
    """
    from datetime import datetime
    
    try:
        datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except ValueError:
        raise AssertionError(f"Invalid timestamp format: {timestamp_str}")


def assert_valid_uuid(uuid_str: str):
    """
    驗證 UUID 格式
    
    Args:
        uuid_str: UUID 字串
    """
    from uuid import UUID
    
    try:
        UUID(uuid_str)
    except ValueError:
        raise AssertionError(f"Invalid UUID format: {uuid_str}")


def assert_stock_data_structure(stock_data: Dict[str, Any]):
    """
    驗證股票數據結構
    
    Args:
        stock_data: 股票數據字典
    """
    required_fields = ["symbol"]
    for field in required_fields:
        assert field in stock_data, \
            f"Stock data missing required field: {field}"
    
    # 價格相關欄位至少要有一個
    price_fields = ["price", "currentPrice", "regularMarketPrice"]
    has_price = any(field in stock_data for field in price_fields)
    assert has_price, \
        f"Stock data should have at least one price field from: {price_fields}"


def assert_user_data_structure(user_data: Dict[str, Any]):
    """
    驗證用戶數據結構
    
    Args:
        user_data: 用戶數據字典
    """
    required_fields = ["user_id", "email", "username"]
    for field in required_fields:
        assert field in user_data, \
            f"User data missing required field: {field}"
    
    # Email 格式驗證
    assert "@" in user_data["email"], \
        "Email should contain '@' symbol"


def assert_token_structure(token_data: Dict[str, Any]):
    """
    驗證認證 Token 結構
    
    Args:
        token_data: Token 數據字典
    """
    required_fields = ["access_token", "token_type"]
    for field in required_fields:
        assert field in token_data, \
            f"Token data missing required field: {field}"
    
    assert token_data["token_type"].lower() == "bearer", \
        "Token type should be 'bearer'"
    
    # Token 應該不為空
    assert len(token_data["access_token"]) > 0, \
        "Access token should not be empty"


def assert_list_response(
    data: Any,
    min_items: int = 0,
    max_items: int = None,
    item_validator: callable = None
):
    """
    驗證列表回應
    
    Args:
        data: 回應數據（應該是列表）
        min_items: 最少項目數
        max_items: 最多項目數
        item_validator: 驗證每個項目的函數
    """
    assert isinstance(data, list), \
        f"Expected list, got {type(data)}"
    
    assert len(data) >= min_items, \
        f"Expected at least {min_items} items, got {len(data)}"
    
    if max_items is not None:
        assert len(data) <= max_items, \
            f"Expected at most {max_items} items, got {len(data)}"
    
    if item_validator and len(data) > 0:
        for i, item in enumerate(data):
            try:
                item_validator(item)
            except AssertionError as e:
                raise AssertionError(f"Item {i} validation failed: {e}")


def extract_error_message(response: Response) -> str:
    """
    從回應中提取錯誤訊息
    
    Args:
        response: HTTP 回應物件
        
    Returns:
        錯誤訊息字串
    """
    try:
        error = response.json()
        
        # 嘗試多種常見錯誤格式
        if isinstance(error, dict):
            return (
                error.get("detail") or
                error.get("message") or
                error.get("error") or
                str(error)
            )
        return str(error)
    except Exception:
        return response.text


def compare_dicts_ignore_keys(
    dict1: Dict[str, Any],
    dict2: Dict[str, Any],
    ignore_keys: List[str] = None
) -> bool:
    """
    比較兩個字典，忽略特定鍵
    
    Args:
        dict1: 第一個字典
        dict2: 第二個字典
        ignore_keys: 要忽略的鍵列表
        
    Returns:
        是否相等
    """
    ignore_keys = ignore_keys or []
    
    keys1 = set(dict1.keys()) - set(ignore_keys)
    keys2 = set(dict2.keys()) - set(ignore_keys)
    
    if keys1 != keys2:
        return False
    
    for key in keys1:
        if dict1[key] != dict2[key]:
            return False
    
    return True
