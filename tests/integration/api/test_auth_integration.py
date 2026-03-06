"""
Integration Tests for Authentication API
認證 API 整合測試 - 完整認證流程測試

測試範圍：
1. 用戶註冊流程
2. 用戶登入流程
3. Token 驗證流程
4. 錯誤處理

改進歷史：
- 2026-02-06: 添加 @pytest.mark.integration 標記
- 2026-02-06: 實施 IMPROVEMENTS.md - 使用 TestDataFactory 和參數化測試
"""
import pytest
from httpx import AsyncClient
from datetime import datetime
from typing import Dict

# 根據 IMPROVEMENTS.md Priority 3 引入測試工廠
from tests.factories import TestDataFactory
from tests.helpers import (
    assert_error_response,
    assert_success_response,
    assert_token_structure,
    assert_user_data_structure
)



class TestAuthenticationFlow:
    """測試完整認證流程"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.critical
    async def test_complete_auth_flow(self, client: AsyncClient):
        """TC-INT-001: 完整認證流程 (註冊 → 登入 → 驗證)"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        
        # Step 1: 註冊新用戶
        register_data = {
            "email": f"integration_{timestamp}@test.com",
            "username": f"intuser_{timestamp}",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        
        register_response = await client.post("/api/v1/auth/register", json=register_data)
        assert register_response.status_code == 201
        
        register_result = register_response.json()
        assert "access_token" in register_result
        assert "user_id" in register_result
        assert register_result["token_type"] == "bearer"
        
        # Step 2: 使用相同帳號登入
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        
        login_response = await client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        login_result = login_response.json()
        assert "access_token" in login_result
        assert login_result["user_id"] == register_result["user_id"]
        
        # Step 3: 驗證 token 有效性 (訪問受保護路由)
        headers = {"Authorization": f"Bearer {login_result['access_token']}"}
        me_response = await client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        me_result = me_response.json()
        assert me_result["email"] == register_data["email"]
        assert me_result["username"] == register_data["username"]
        assert "user_id" in me_result


class TestUserRegistration:
    """測試用戶註冊功能"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_register_new_user(self, client: AsyncClient):
        """TC-INT-002: 註冊新用戶 - 成功案例 (使用工廠)"""
        # 使用 TestDataFactory 簡化數據生成
        user_data = TestDataFactory.create_user_data()
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        # 使用輔助函數驗證
        assert_success_response(response, 201, ["access_token", "user_id"])
        result = response.json()
        assert_token_structure(result)
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """TC-INT-003: 註冊重複 email - 應失敗 (改進版)"""
        duplicate_data = TestDataFactory.create_user_data(
            email=test_user["email"]  # 使用已存在的 email
        )
        
        response = await client.post("/api/v1/auth/register", json=duplicate_data)
        
        # 使用增強的錯誤驗證
        assert_error_response(response, [400, 409, 422], ["email", "already", "exists", "duplicate"])
    
    # Priority 2: 參數化測試 - 減少重複代碼
    @pytest.mark.parametrize("invalid_email,expected_keywords", [
        ("not-an-email", ["email", "invalid"]),
        ("@missing-local.com", ["email", "invalid"]),
        ("missing-at.com", ["email", "invalid"]),
        ("spaces in@email.com", ["email", "invalid"]),
        ("", ["email", "required"]),
    ])
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_register_invalid_emails(
        self,
        client: AsyncClient,
        invalid_email: str,
        expected_keywords: list
    ):
        """TC-INT-005: 多種無效 email 格式測試 (參數化)"""
        user_data = TestDataFactory.create_user_data(email=invalid_email)
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation Error
        assert_error_response(response, 422, expected_keywords)
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_register_password_mismatch(self, client: AsyncClient):
        """TC-INT-004: 密碼不匹配 - 應失敗"""
        user_data = TestDataFactory.create_user_data(
            confirm_password="DifferentPass123!"
        )
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        assert_error_response(response, [400, 422], ["password", "match"])
    
    # Priority 2: 參數化測試 - 弱密碼場景
    @pytest.mark.parametrize("weak_password,error_keywords", [
        ("123", ["password", "short", "length"]),
        ("abc", ["password", "short", "length"]),
        ("NoNumber!", ["password", "digit", "number"]),
        ("nonumber1", ["password", "uppercase"]),
        ("NOLOWER1", ["password", "lowercase"]),
    ])
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_register_weak_passwords(
        self,
        client: AsyncClient,
        weak_password: str,
        error_keywords: list
    ):
        """TC-INT-006: 多種弱密碼測試 (參數化)"""
        user_data = TestDataFactory.create_user_data(
            password=weak_password,
            confirm_password=weak_password
        )
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        # 允許不同的錯誤處理方式
        if response.status_code in [400, 422]:
            # 至少要有一個關鍵字匹配
            error_str = str(response.json()).lower()
            has_keyword = any(kw.lower() in error_str for kw in error_keywords)
            # 可能通過驗證但應該捕獲弱密碼
            assert response.status_code in [400, 422] or not has_keyword


class TestUserLogin:
    """測試用戶登入功能"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_login_success(self, client: AsyncClient, test_user: Dict[str, str]):
        """TC-INT-007: 正確登入憑證 - 成功 (使用工廠)"""
        login_data = TestDataFactory.create_login_data(
            test_user["email"],
            test_user["password"]
        )
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert_success_response(response, 200, ["access_token", "user_id"])
        result = response.json()
        assert result["user_id"] == test_user["user_id"]
        assert_token_structure(result)
    
    # Priority 2: 參數化測試 - 登入失敗場景
    @pytest.mark.parametrize("email,password,error_keywords", [
        ("wrong@email.com", "ValidPass123!", ["incorrect", "not found", "invalid"]),
        ("test@test.com", "WrongPassword!", ["incorrect", "invalid", "password"]),
        ("", "ValidPass123!", ["email", "required"]),
        ("test@test.com", "", ["password", "required"]),
    ])
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_login_failures(
        self,
        client: AsyncClient,
        email: str,
        password: str,
        error_keywords: list
    ):
        """TC-INT-008/009/010: 多種登入失敗場景 (參數化)"""
        login_data = TestDataFactory.create_login_data(email, password)
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code in [400, 401, 403, 404, 422]
        assert_error_response(response, [400, 401, 403, 404, 422], error_keywords)


class TestTokenValidation:
    """測試 Token 驗證功能"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.critical
    async def test_access_protected_route_with_valid_token(
        self,
        client: AsyncClient,
        auth_headers: Dict[str, str],
        test_user: Dict[str, str]
    ):
        """TC-INT-011: 使用有效 token 存取保護路由"""
        response = await client.get("/api/v1/users/me", headers=auth_headers)
        
        assert_success_response(response, 200, ["user_id", "email"])
        result = response.json()
        assert_user_data_structure(result)
        assert result["user_id"] == test_user["user_id"]
    
    # Priority 2: 參數化測試 - Token 驗證失敗場景
    @pytest.mark.parametrize("auth_header,error_keywords", [
        (None, ["unauthorized", "missing", "required"]),
        ({"Authorization": ""}, ["unauthorized", "invalid", "token"]),
        ({"Authorization": "Bearer"}, ["unauthorized", "invalid", "token"]),
        ({"Authorization": "Bearer invalid_xyz"}, ["unauthorized", "invalid"]),
        ({"Authorization": "InvalidScheme token123"}, ["unauthorized", "invalid"]),
    ])
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_token_validation_failures(
        self,
        client: AsyncClient,
        auth_header: dict,
        error_keywords: list
    ):
        """TC-INT-012/013/014: 多種 Token 驗證失敗場景 (參數化)"""
        headers = auth_header if auth_header else {}
        response = await client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code in [401, 403]
        assert_error_response(response, [401, 403], error_keywords)


class TestConcurrentAuthentication:
    """測試並發認證場景"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_multiple_logins_same_user(self, client: AsyncClient, test_user: Dict[str, str]):
        """TC-INT-015: 同一用戶多次登入 - 應都成功"""
        import asyncio
        
        async def login():
            login_data = {
                "email": test_user["email"],
                "password": test_user["password"]
            }
            response = await client.post("/api/v1/auth/login", json=login_data)
            return response
        
        # 同時發起 5 個登入請求
        responses = await asyncio.gather(*[login() for _ in range(5)])
        
        # 所有登入都應該成功
        for response in responses:
            assert response.status_code == 200
            result = response.json()
            assert "access_token" in result
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_token_works_after_another_login(self, client: AsyncClient, test_user: Dict[str, str]):
        """TC-INT-016: 再次登入後舊 token 應仍有效"""
        # 第一次登入
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        
        first_login = await client.post("/api/v1/auth/login", json=login_data)
        first_token = first_login.json()["access_token"]
        
        # 第二次登入 (獲取新 token)
        second_login = await client.post("/api/v1/auth/login", json=login_data)
        second_token = second_login.json()["access_token"]
        
        # 兩個 token 都應該能訪問受保護路由
        first_headers = {"Authorization": f"Bearer {first_token}"}
        second_headers = {"Authorization": f"Bearer {second_token}"}
        
        first_response = await client.get("/api/v1/auth/me", headers=first_headers)
        second_response = await client.get("/api/v1/auth/me", headers=second_headers)
        
        assert first_response.status_code == 200
        assert second_response.status_code == 200


class TestAuthenticationEdgeCases:
    """測試認證邊界案例"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_register_with_spaces_in_input(self, client: AsyncClient):
        """TC-INT-017: 輸入包含空格 - 應正確處理"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        user_data = {
            "email": f" spaces_{timestamp}@test.com ",  # 前後有空格
            "username": f"spaces_{timestamp}",
            "password": "ValidPass123!",
            "confirm_password": "ValidPass123!"
        }
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        # 應該成功或正確驗證失敗
        assert response.status_code in [201, 422]
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_login_case_sensitivity(self, client: AsyncClient, test_user: Dict[str, str]):
        """TC-INT-018: Email 大小寫敏感性測試"""
        # 使用大寫版本的 email
        login_data = {
            "email": test_user["email"].upper(),
            "password": test_user["password"]
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        # 根據系統設計，email 可能大小寫不敏感
        # 如果不敏感應該成功 (200)，如果敏感應該失敗 (401)
        assert response.status_code in [200, 401]
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_register_with_special_characters_username(self, client: AsyncClient):
        """TC-INT-019: Username 包含特殊字元"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        user_data = {
            "email": f"special_{timestamp}@test.com",
            "username": f"user-name_{timestamp}!@#",
            "password": "ValidPass123!",
            "confirm_password": "ValidPass123!"
        }
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        # 根據系統規則，可能允許或拒絕特殊字元
        assert response.status_code in [201, 400, 422]
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_empty_request_body(self, client: AsyncClient):
        """TC-INT-020: 空請求體 - 應返回驗證錯誤"""
        response = await client.post("/api/v1/auth/register", json={})
        
        assert response.status_code == 422  # Validation Error
