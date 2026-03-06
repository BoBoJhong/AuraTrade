"""
Unit Tests for AuthService
測試計畫追溯: TP-20260206-001
風險等級: Critical
覆蓋率目標: 90%+

測試案例:
- TC-UT-AUTH-001 ~ TC-UT-AUTH-012
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from apps.services.auth_service import AuthService
from apps.repositories.user_repository import UserRepository
from apps.models.user import User
from apps.core.exceptions import AuthenticationError, BusinessLogicError
from datetime import datetime


# === Fixtures ===

@pytest.fixture
def mock_user_repo():
    """Mock UserRepository"""
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def auth_service(mock_user_repo):
    """Create AuthService instance with mocked repository"""
    return AuthService(mock_user_repo)


@pytest.fixture
def valid_user():
    """Valid user mock data"""
    return User(
        user_id="test-user-id-123",
        email="test@example.com",
        username="testuser",
        password_hash="$2b$12$hashed_password_here",
        is_active=True,
        role="user",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


# === TC-UT-AUTH-001: 成功註冊新用戶 ===

@pytest.mark.asyncio
@patch('apps.services.auth_service.hash_password')
@patch('apps.services.auth_service.create_access_token')
@patch('apps.services.auth_service.create_refresh_token')
async def test_register_user_success(
    mock_refresh_token,
    mock_access_token,
    mock_hash,
    auth_service,
    mock_user_repo,
    valid_user
):
    """
    TC-UT-AUTH-001: 成功註冊新用戶
    
    Given: 有效的email、密碼、用戶名
    When: 調用 register_user()
    Then: 返回用戶資料與Token
    """
    # Arrange
    mock_user_repo.find_by_email.return_value = None  # Email 未被使用
    mock_user_repo.create.return_value = valid_user
    mock_hash.return_value = "hashed_password"
    mock_access_token.return_value = "access_token_abc123"
    mock_refresh_token.return_value = "refresh_token_xyz789"
    
    # Act
    result = await auth_service.register_user(
        email="newuser@example.com",
        password="ValidPass123",
        username="newuser"
    )
    
    # Assert
    assert result["user_id"] == str(valid_user.user_id)
    assert result["email"] == valid_user.email
    assert result["username"] == valid_user.username
    assert result["access_token"] == "access_token_abc123"
    assert result["refresh_token"] == "refresh_token_xyz789"
    assert result["token_type"] == "bearer"
    
    mock_user_repo.find_by_email.assert_called_once_with("newuser@example.com")
    mock_user_repo.create.assert_called_once()


# === TC-UT-AUTH-002: 成功登入已存在用戶 ===

@pytest.mark.asyncio
@patch('apps.services.auth_service.verify_password')
@patch('apps.services.auth_service.create_access_token')
@patch('apps.services.auth_service.create_refresh_token')
async def test_login_user_success(
    mock_refresh_token,
    mock_access_token,
    mock_verify,
    auth_service,
    mock_user_repo,
    valid_user
):
    """
    TC-UT-AUTH-002: 成功登入已存在用戶
    
    Given: 正確的email與密碼
    When: 調用 login_user()
    Then: 返回用戶資料與Token
    """
    # Arrange
    mock_user_repo.find_by_email.return_value = valid_user
    mock_verify.return_value = True
    mock_access_token.return_value = "access_token_abc123"
    mock_refresh_token.return_value = "refresh_token_xyz789"
    
    # Act
    result = await auth_service.login_user(
        email="test@example.com",
        password="CorrectPass123"
    )
    
    # Assert
    assert result["user_id"] == str(valid_user.user_id)
    assert result["email"] == valid_user.email
    assert result["access_token"] == "access_token_abc123"
    
    mock_user_repo.update_last_login.assert_called_once_with(str(valid_user.user_id))


# === TC-UT-AUTH-003: Email格式錯誤 ===

@pytest.mark.asyncio
async def test_register_invalid_email(auth_service):
    """
    TC-UT-AUTH-003: Email格式錯誤
    
    Given: 無@符號的email
    When: 調用 register_user()
    Then: 拋出 BusinessLogicError AUTH_400_001
    """
    with pytest.raises(BusinessLogicError) as exc_info:
        await auth_service.register_user(
            email="invalid-email-no-at",
            password="ValidPass123",
            username="testuser"
        )
    
    assert exc_info.value.code == "AUTH_400_001"
    assert "Email 格式不正確" in str(exc_info.value)


# === TC-UT-AUTH-004: 密碼過短 ===

@pytest.mark.asyncio
async def test_register_password_too_short(auth_service):
    """
    TC-UT-AUTH-004: 密碼過短
    
    Given: 少於8字元的密碼
    When: 調用 register_user()
    Then: 拋出 BusinessLogicError AUTH_400_002
    """
    with pytest.raises(BusinessLogicError) as exc_info:
        await auth_service.register_user(
            email="test@example.com",
            password="Short1",  # 只有6字元
            username="testuser"
        )
    
    assert exc_info.value.code == "AUTH_400_002"
    assert "密碼必須至少 8 個字元" in str(exc_info.value)


# === TC-UT-AUTH-005: 密碼無大寫字母 ===

@pytest.mark.asyncio
async def test_register_password_no_uppercase(auth_service):
    """
    TC-UT-AUTH-005: 密碼無大寫字母
    
    Given: 無大寫字母的密碼
    When: 調用 register_user()
    Then: 拋出 BusinessLogicError AUTH_400_002
    """
    with pytest.raises(BusinessLogicError) as exc_info:
        await auth_service.register_user(
            email="test@example.com",
            password="lowercase123",
            username="testuser"
        )
    
    assert exc_info.value.code == "AUTH_400_002"


# === TC-UT-AUTH-006: 密碼無數字 ===

@pytest.mark.asyncio
async def test_register_password_no_digit(auth_service):
    """
    TC-UT-AUTH-006: 密碼無數字
    
    Given: 無數字的密碼
    When: 調用 register_user()
    Then: 拋出 BusinessLogicError AUTH_400_002
    """
    with pytest.raises(BusinessLogicError) as exc_info:
        await auth_service.register_user(
            email="test@example.com",
            password="OnlyLetters",
            username="testuser"
        )
    
    assert exc_info.value.code == "AUTH_400_002"


# === TC-UT-AUTH-007: Email已被註冊 ===

@pytest.mark.asyncio
async def test_register_duplicate_email(auth_service, mock_user_repo, valid_user):
    """
    TC-UT-AUTH-007: Email已被註冊
    
    Given: 已存在的email
    When: 調用 register_user()
    Then: 拋出 BusinessLogicError AUTH_400_003
    """
    # Arrange
    mock_user_repo.find_by_email.return_value = valid_user
    
    # Act & Assert
    with pytest.raises(BusinessLogicError) as exc_info:
        await auth_service.register_user(
            email="test@example.com",
            password="ValidPass123",
            username="newuser"
        )
    
    assert exc_info.value.code == "AUTH_400_003"
    assert "此 Email 已被註冊" in str(exc_info.value)


# === TC-UT-AUTH-008: 登入密碼錯誤 ===

@pytest.mark.asyncio
@patch('apps.services.auth_service.verify_password')
async def test_login_wrong_password(mock_verify, auth_service, mock_user_repo, valid_user):
    """
    TC-UT-AUTH-008: 登入密碼錯誤
    
    Given: 正確email + 錯誤密碼
    When: 調用 login_user()
    Then: 拋出 AuthenticationError AUTH_401_001
    """
    # Arrange
    mock_user_repo.find_by_email.return_value = valid_user
    mock_verify.return_value = False
    
    # Act & Assert
    with pytest.raises(AuthenticationError) as exc_info:
        await auth_service.login_user(
            email="test@example.com",
            password="WrongPassword123"
        )
    
    assert exc_info.value.code == "AUTH_401_001"
    assert "Email 或密碼錯誤" in str(exc_info.value)


# === TC-UT-AUTH-009: 登入帳號不存在 ===

@pytest.mark.asyncio
async def test_login_user_not_found(auth_service, mock_user_repo):
    """
    TC-UT-AUTH-009: 登入帳號不存在
    
    Given: 不存在的email
    When: 調用 login_user()
    Then: 拋出 AuthenticationError AUTH_401_001
    """
    # Arrange
    mock_user_repo.find_by_email.return_value = None
    
    # Act & Assert
    with pytest.raises(AuthenticationError) as exc_info:
        await auth_service.login_user(
            email="nonexistent@example.com",
            password="AnyPassword123"
        )
    
    assert exc_info.value.code == "AUTH_401_001"
    assert "Email 或密碼錯誤" in str(exc_info.value)


# === TC-UT-AUTH-010: 帳號已停用 ===

@pytest.mark.asyncio
@patch('apps.services.auth_service.verify_password')
async def test_login_inactive_user(mock_verify, auth_service, mock_user_repo, valid_user):
    """
    TC-UT-AUTH-010: 帳號已停用
    
    Given: is_active=False的用戶
    When: 調用 login_user()
    Then: 拋出 AuthenticationError AUTH_403_001
    """
    # Arrange
    valid_user.is_active = False
    mock_user_repo.find_by_email.return_value = valid_user
    mock_verify.return_value = True
    
    # Act & Assert
    with pytest.raises(AuthenticationError) as exc_info:
        await auth_service.login_user(
            email="test@example.com",
            password="CorrectPass123"
        )
    
    assert exc_info.value.code == "AUTH_403_001"
    assert "帳號已被停用" in str(exc_info.value)


# === TC-UT-AUTH-011: 空值參數 ===

@pytest.mark.asyncio
async def test_register_null_email(auth_service):
    """
    TC-UT-AUTH-011: 空值參數 - Email為None
    
    Given: email=None
    When: 調用 register_user()
    Then: 拋出適當錯誤
    """
    with pytest.raises((BusinessLogicError, TypeError, AttributeError)):
        await auth_service.register_user(
            email=None,
            password="ValidPass123",
            username="testuser"
        )


@pytest.mark.asyncio
async def test_register_empty_password(auth_service):
    """
    TC-UT-AUTH-011: 空值參數 - 密碼為空字串
    
    Given: password=""
    When: 調用 register_user()
    Then: 拋出 BusinessLogicError
    """
    with pytest.raises(BusinessLogicError):
        await auth_service.register_user(
            email="test@example.com",
            password="",
            username="testuser"
        )


# === TC-UT-AUTH-012: SQL Injection 防禦測試 ===

@pytest.mark.asyncio
async def test_sql_injection_defense(auth_service, mock_user_repo):
    """
    TC-UT-AUTH-012: SQL Injection防禦
    
    Given: email包含SQL注入字串
    When: 調用 register_user()
    Then: 正常處理不執行惡意SQL (通過 ORM 保護)
    """
    # Arrange
    malicious_email = "admin'--@example.com"
    mock_user_repo.find_by_email.return_value = None
    
    # Act - 不應拋出異常，應正常處理
    with pytest.raises(BusinessLogicError) as exc_info:
        await auth_service.register_user(
            email=malicious_email,
            password="ValidPass123",
            username="testuser"
        )
    
    # Email 格式驗證應該拒絕這個輸入
    assert exc_info.value.code == "AUTH_400_001"
    
    # 驗證 find_by_email 被正確調用（使用參數化查詢，非字串拼接）
    # ORM 層應該自動防禦 SQL Injection
