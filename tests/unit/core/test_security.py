"""
Unit Tests for Security Module
測試計畫追溯: TP-20260206-001
風險等級: Critical
覆蓋率目標: 90%+

測試案例:
- TC-UT-SEC-001 ~ TC-UT-SEC-010
"""
import pytest
from datetime import timedelta, datetime
from jose import jwt, JWTError
from apps.core import security
from apps.core.config import settings


# === TC-UT-SEC-001: 正確雜湊密碼 ===

def test_hash_password_success():
    """
    TC-UT-SEC-001: 正確雜湊密碼
    
    Given: 有效的明文密碼
    When: 調用 hash_password()
    Then: 返回 bcrypt 雜湊值
    """
    # Arrange
    password = "MySecurePassword123"
    
    # Act
    hashed = security.hash_password(password)
    
    # Assert
    assert isinstance(hashed, str)
    assert hashed.startswith("$2b$")  # Bcrypt 格式
    assert len(hashed) == 60  # Bcrypt 固定長度
    assert hashed != password  # 不是明文


# === TC-UT-SEC-002: 驗證正確密碼 ===

def test_verify_password_correct():
    """
    TC-UT-SEC-002: 驗證正確密碼
    
    Given: 明文密碼與對應的雜湊
    When: 調用 verify_password()
    Then: 返回 True
    """
    # Arrange
    password = "MySecurePassword123"
    hashed = security.hash_password(password)
    
    # Act
    result = security.verify_password(password, hashed)
    
    # Assert
    assert result is True


# === TC-UT-SEC-003: 拒絕錯誤密碼 ===

def test_verify_password_incorrect():
    """
    TC-UT-SEC-003: 拒絕錯誤密碼
    
    Given: 明文密碼與不匹配的雜湊
    When: 調用 verify_password()
    Then: 返回 False
    """
    # Arrange
    correct_password = "MySecurePassword123"
    wrong_password = "WrongPassword456"
    hashed = security.hash_password(correct_password)
    
    # Act
    result = security.verify_password(wrong_password, hashed)
    
    # Assert
    assert result is False


# === TC-UT-SEC-004: 處理超長密碼 (> 72 bytes) ===

def test_hash_password_long():
    """
    TC-UT-SEC-004: 處理超長密碼
    
    Given: 超過 72 bytes 的密碼
    When: 調用 hash_password()
    Then: 正常處理（自動截斷至72 bytes）
    """
    # Arrange
    # 建立一個 80 bytes 的密碼
    long_password = "A" * 80
    
    # Act
    hashed = security.hash_password(long_password)
    
    # Assert
    assert isinstance(hashed, str)
    assert hashed.startswith("$2b$")
    
    # 驗證前72字元可以通過驗證
    assert security.verify_password(long_password, hashed) is True


# === TC-UT-SEC-005: 處理特殊字元密碼 ===

def test_hash_password_special_chars():
    """
    TC-UT-SEC-005: 處理特殊字元密碼
    
    Given: 包含特殊字元的密碼
    When: 調用 hash_password()
    Then: 正常處理並可驗證
    """
    # Arrange
    special_password = "P@ssw0rd!#$%&*()[]{}:;<>?/\\|`~"
    
    # Act
    hashed = security.hash_password(special_password)
    
    # Assert
    assert security.verify_password(special_password, hashed) is True


# === TC-UT-SEC-006: 生成有效 Access Token ===

def test_create_access_token_success():
    """
    TC-UT-SEC-006: 生成有效 Access Token
    
    Given: 用戶資料 (user_id, email, role)
    When: 調用 create_access_token()
    Then: 返回有效的 JWT Token
    """
    # Arrange
    data = {
        "sub": "user-id-123",
        "email": "test@example.com",
        "role": "user"
    }
    
    # Act
    token = security.create_access_token(data)
    
    # Assert
    assert isinstance(token, str)
    assert len(token) > 50  # JWT 通常較長
    
    # 解碼驗證
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "user-id-123"
    assert payload["email"] == "test@example.com"
    assert payload["role"] == "user"
    assert payload["type"] == "access"
    assert "exp" in payload  # 包含過期時間


# === TC-UT-SEC-007: 驗證有效 Token ===

def test_decode_token_valid():
    """
    TC-UT-SEC-007: 驗證有效 Token
    
    Given: 剛生成的有效 Token
    When: 調用 decode_token()
    Then: 返回正確的 payload
    """
    # Arrange
    data = {"sub": "user-id-123", "email": "test@example.com"}
    token = security.create_access_token(data)
    
    # Act
    payload = security.decode_token(token)
    
    # Assert
    assert payload["sub"] == "user-id-123"
    assert payload["email"] == "test@example.com"
    assert payload["type"] == "access"


# === TC-UT-SEC-008: 拒絕過期 Token ===

def test_decode_token_expired():
    """
    TC-UT-SEC-008: 拒絕過期 Token
    
    Given: 已過期的 Token
    When: 調用 decode_token()
    Then: 拋出 JWTError
    """
    # Arrange
    data = {"sub": "user-id-123"}
    # 創建一個立即過期的 Token
    expired_token = security.create_access_token(
        data, 
        expires_delta=timedelta(seconds=-1)  # 負數表示已過期
    )
    
    # Act & Assert
    with pytest.raises(JWTError):
        security.decode_token(expired_token)


# === TC-UT-SEC-009: 拒絕偽造 Token ===

def test_decode_token_forged():
    """
    TC-UT-SEC-009: 拒絕偽造 Token
    
    Given: 使用錯誤 SECRET_KEY 的 Token
    When: 調用 decode_token()
    Then: 拋出 JWTError
    """
    # Arrange
    fake_secret = "WRONG_SECRET_KEY_12345"
    data = {"sub": "user-id-123", "exp": datetime.utcnow() + timedelta(minutes=30)}
    
    # 使用錯誤的 SECRET_KEY 生成 Token
    forged_token = jwt.encode(data, fake_secret, algorithm=settings.ALGORITHM)
    
    # Act & Assert
    with pytest.raises(JWTError):
        security.decode_token(forged_token)


# === TC-UT-SEC-010: 拒絕格式錯誤 Token ===

def test_decode_token_malformed():
    """
    TC-UT-SEC-010: 拒絕格式錯誤 Token
    
    Given: 格式錯誤的 Token 字串
    When: 調用 decode_token()
    Then: 拋出 JWTError
    """
    # Arrange
    malformed_tokens = [
        "not.a.jwt.token",
        "invalid_format",
        "eyJhbGciOiJIUzI1.incomplete",
        "",
        "Bearer eyJhbGciOiJI",  # 包含 Bearer 前綴
    ]
    
    # Act & Assert
    for token in malformed_tokens:
        with pytest.raises((JWTError, ValueError, AttributeError)):
            security.decode_token(token)


# === Bonus: Refresh Token 測試 ===

def test_create_refresh_token():
    """
    Bonus: 測試 Refresh Token 生成
    
    Given: 用戶資料
    When: 調用 create_refresh_token()
    Then: 返回有效的 refresh token，過期時間更長
    """
    # Arrange
    data = {"sub": "user-id-123"}
    
    # Act
    refresh_token = security.create_refresh_token(data)
    
    # Assert
    payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "user-id-123"
    assert payload["type"] == "refresh"
    
    # 驗證過期時間 (應該比 access token 長)
    refresh_exp = datetime.utcfromtimestamp(payload["exp"])
    access_token = security.create_access_token(data)
    access_payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    access_exp = datetime.utcfromtimestamp(access_payload["exp"])
    
    assert refresh_exp > access_exp  # Refresh token 過期時間更長


# === Bonus: 測試密碼不可逆 ===

def test_hash_password_one_way():
    """
    Bonus: 測試密碼雜湊的不可逆性
    
    Given: 同樣的密碼
    When: 多次雜湊
    Then: 每次得到不同的雜湊值 (因為隨機 salt)
    """
    # Arrange
    password = "MyPassword123"
    
    # Act
    hash1 = security.hash_password(password)
    hash2 = security.hash_password(password)
    
    # Assert
    assert hash1 != hash2  # 雜湊值不同 (隨機 salt)
    assert security.verify_password(password, hash1) is True
    assert security.verify_password(password, hash2) is True
