"""Create price alerts table

Revision ID: 004
Revises: 002
Create Date: 2026-01-30 13:52:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create price_alerts table
    op.create_table(
        'price_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('alert_type', sa.String(length=20), nullable=False, comment='提醒類型: price_above, price_below, percent_up, percent_down'),
        sa.Column('target_value', sa.Float(), nullable=False, comment='目標值 (價格或百分比)'),
        sa.Column('base_price', sa.Float(), nullable=True, comment='基準價格 (用於計算百分比漲跌)'),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True, comment='是否啟用'),
        sa.Column('is_triggered', sa.Boolean(), nullable=True, default=False, comment='是否已觸發'),
        sa.Column('triggered_at', sa.DateTime(), nullable=True, comment='觸發時間'),
        sa.Column('message', sa.String(length=255), nullable=True, comment='自訂提醒訊息'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['symbol'], ['stocks.symbol'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_price_alerts_id'), 'price_alerts', ['id'], unique=False)
    op.create_index('ix_price_alerts_user_id', 'price_alerts', ['user_id'], unique=False)
    op.create_index('ix_price_alerts_symbol', 'price_alerts', ['symbol'], unique=False)
    op.create_index('ix_price_alerts_active', 'price_alerts', ['is_active'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_price_alerts_active', table_name='price_alerts')
    op.drop_index('ix_price_alerts_symbol', table_name='price_alerts')
    op.drop_index('ix_price_alerts_user_id', table_name='price_alerts')
    op.drop_index(op.f('ix_price_alerts_id'), table_name='price_alerts')
    op.drop_table('price_alerts')
