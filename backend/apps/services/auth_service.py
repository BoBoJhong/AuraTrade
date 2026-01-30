"""
Authentication Service
追溯: REQ-012, REQ-013, REQ-014
"""
from apps.repositories.user_repository import UserRepository
from apps.models.user import User
from apps.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from apps.core.exceptions import AuthenticationError, BusinessLogicError
from datetime import timedelta
import re


class AuthService:
    """認證業務邏輯層"""
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def register_user(self, email: str, password: str, username: str) -> dict:
        """
        用戶註冊
        追溯: REQ-012, US-12
        """
        # 驗證 Email 格式
        if not self._is_valid_email(email):
            raise BusinessLogicError("Email 格式不正確", code="AUTH_400_001")
        
        # 驗證密碼強度
        if not self._is_valid_password(password):
            raise BusinessLogicError(
                "密碼必須至少 8 個字元，包含大小寫字母與數字",
                code="AUTH_400_002"
            )
        
        # 檢查 Email 是否已存在
        existing_user = await self.user_repo.find_by_email(email)
        if existing_user:
            raise BusinessLogicError("此 Email 已被註冊", code="AUTH_400_003")
        
        # 創建新用戶
        hashed_password = hash_password(password)
        new_user = User(
            email=email,
            password_hash=hashed_password,
            username=username
        )
        
        created_user = await self.user_repo.create(new_user)
        
        # 生成 Token
        access_token = create_access_token(
            data={"sub": str(created_user.user_id), "email": email, "role": created_user.role}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(created_user.user_id)}
        )
        
        return {
            "user_id": str(created_user.user_id),
            "email": created_user.email,
            "username": created_user.username,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    async def login_user(self, email: str, password: str) -> dict:
        """
        用戶登入
        追溯: REQ-013, US-12
        """
        # 查找用戶
        user = await self.user_repo.find_by_email(email)
        if not user:
            raise AuthenticationError("Email 或密碼錯誤", code="AUTH_401_001")
        
        # 驗證密碼
        if not verify_password(password, user.password_hash):
            raise AuthenticationError("Email 或密碼錯誤", code="AUTH_401_001")
        
        # 檢查帳號狀態
        if not user.is_active:
            raise AuthenticationError("帳號已被停用", code="AUTH_403_001")
        
        # 更新最後登入時間
        await self.user_repo.update_last_login(str(user.user_id))
        
        # 生成 Token
        access_token = create_access_token(
            data={"sub": str(user.user_id), "email": user.email, "role": user.role}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.user_id)}
        )
        
        return {
            "user_id": str(user.user_id),
            "email": user.email,
            "username": user.username,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    def _is_valid_email(self, email: str) -> bool:
        """驗證 Email 格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _is_valid_password(self, password: str) -> bool:
        """
        驗證密碼強度 - BR-07
        至少 8 個字元，包含大小寫字母與數字
        """
        if len(password) < 8:
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        return True
