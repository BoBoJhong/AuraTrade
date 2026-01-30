"""Create stock monitoring tables

Revision ID: 002
Revises: 001
Create Date: 2026-01-29 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create stocks table
    op.create_table(
        'stocks',
        sa.Column('symbol', sa.String(length=20), nullable=False, comment='股票代碼 (e.g. 2330.TW)'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='股票名稱'),
        sa.Column('market', sa.String(length=10), nullable=False, comment='市場 (TW, US)'),
        sa.Column('sector', sa.String(length=50), nullable=True, comment='產業類別'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('symbol')
    )
    op.create_index(op.f('ix_stocks_symbol'), 'stocks', ['symbol'], unique=False)

    # Create watchlists table
    op.create_table(
        'watchlists',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('target_price', sa.Float(), nullable=True, comment='目標價格 (預警用)'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['symbol'], ['stocks.symbol'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'symbol', name='uq_user_stock')
    )
    op.create_index(op.f('ix_watchlists_id'), 'watchlists', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_watchlists_id'), table_name='watchlists')
    op.drop_table('watchlists')
    op.drop_index(op.f('ix_stocks_symbol'), table_name='stocks')
    op.drop_table('stocks')
