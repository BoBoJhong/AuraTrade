"""Create users table

Revision ID: 001
Revises: 
Create Date: 2026-01-29 14:23:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create users table with all required fields."""
    op.create_table(
        'users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, comment='用戶唯一識別碼'),
        sa.Column('email', sa.String(length=255), nullable=False, comment='用戶 Email'),
        sa.Column('password_hash', sa.String(length=255), nullable=False, comment='bcrypt 加密密碼'),
        sa.Column('username', sa.String(length=100), nullable=False, comment='用戶名稱'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False, comment='註冊時間'),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True, comment='最後更新時間'),
        sa.Column('last_login_at', sa.TIMESTAMP(timezone=True), nullable=True, comment='最後登入時間'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='帳號是否啟用'),
        sa.Column('role', sa.String(length=20), nullable=False, server_default=sa.text("'user'"), comment='用戶角色 (user/admin)'),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('email')
    )
    
    # Create index on email for faster lookups
    op.create_index('ix_users_email', 'users', ['email'], unique=True)


def downgrade() -> None:
    """Drop users table and its indexes."""
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
