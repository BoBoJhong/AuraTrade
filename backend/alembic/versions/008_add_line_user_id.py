"""Add LINE user_id for Messaging API

Revision ID: 008
Revises: 007
Create Date: 2026-01-30 23:58:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    # Add LINE user_id column
    op.add_column('users', sa.Column('line_user_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('line_notify_enabled', sa.Boolean(), server_default='false', nullable=False))
    
    # Create index for faster lookup
    op.create_index(op.f('ix_users_line_user_id'), 'users', ['line_user_id'], unique=True)


def downgrade():
    # Remove index and columns
    op.drop_index(op.f('ix_users_line_user_id'), table_name='users')
    op.drop_column('users', 'line_notify_enabled')
    op.drop_column('users', 'line_user_id')
