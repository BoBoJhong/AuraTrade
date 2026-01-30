"""
User Repository
追溯: REQ-012, REQ-013
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from apps.models.user import User
from typing import Optional
from datetime import datetime


class UserRepository:
    """用戶資料存取層"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """根據 Email 查詢用戶"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """根據 user_id 查詢用戶"""
        result = await self.db.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, user: User) -> User:
        """創建新用戶"""
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update_last_login(self, user_id: str) -> None:
        """更新最後登入時間"""
        user = await self.find_by_id(user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            await self.db.commit()
