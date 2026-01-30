"""
User Profile API Routes

Protected endpoints for user profile management.
"""
from fastapi import APIRouter, Depends
from apps.core.dependencies import get_current_active_user
from apps.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user's profile.
    
    This endpoint requires valid JWT authentication.
    
    Returns:
        User profile information
    """
    return {
        "user_id": str(current_user.user_id),
        "email": current_user.email,
        "username": current_user.username,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat(),
        "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None
    }
