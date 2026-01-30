"""
User Model
追溯: REQ-012, REQ-088
"""
from sqlalchemy import Column, String, Boolean, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from apps.core.database import Base
import uuid


class User(Base):
    """
    用戶資料表
    追溯: SRS Section 3.4, SDD Section 5.2
    """
    __tablename__ = "users"
    
    user_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="用戶唯一識別碼"
    )
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="用戶 Email"
    )
    password_hash = Column(
        String(255),
        nullable=False,
        comment="bcrypt 加密密碼"
    )
    username = Column(
        String(100),
        nullable=False,
        comment="用戶名稱"
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="註冊時間"
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="最後更新時間"
    )
    last_login_at = Column(
        TIMESTAMP(timezone=True),
        comment="最後登入時間"
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="帳號是否啟用"
    )
    role = Column(
        String(20),
        default="user",
        nullable=False,
        comment="用戶角色 (user/admin)"
    )
    line_user_id = Column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
        comment="LINE Bot 用戶 ID（用於推播通知）"
    )
    line_notify_enabled = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否啟用 LINE 通知"
    )
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, email={self.email})>"
