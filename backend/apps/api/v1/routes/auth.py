"""
Authentication API Routes
追溯: REQ-012, REQ-013
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from apps.api.v1.schemas.auth import UserRegisterRequest, UserLoginRequest, AuthResponse
from apps.services.auth_service import AuthService
from apps.repositories.user_repository import UserRepository
from apps.core.database import get_db
from apps.core.exceptions import AuraTradeException
from apps.core.dependencies import get_current_user
from apps.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    用戶註冊
    追溯: REQ-012, US-12
    """
    try:
        user_repo = UserRepository(db)
        auth_service = AuthService(user_repo)
        result = await auth_service.register_user(
            email=request.email,
            password=request.password,
            username=request.username
        )
        return result
    except AuraTradeException as e:
        raise HTTPException(status_code=e.status_code, detail={
            "code": e.code,
            "message": e.message
        })


@router.post("/login", response_model=AuthResponse)
async def login(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    用戶登入
    追溯: REQ-013, US-12
    """
    try:
        user_repo = UserRepository(db)
        auth_service = AuthService(user_repo)
        result = await auth_service.login_user(
            email=request.email,
            password=request.password
        )
        return result
    except AuraTradeException as e:
        raise HTTPException(status_code=e.status_code, detail={
            "code": e.code,
            "message": e.message
        })


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """取得當前用戶資訊"""
    return {
        "user_id": str(current_user.user_id),
        "email": current_user.email,
        "username": current_user.username,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat()
    }
