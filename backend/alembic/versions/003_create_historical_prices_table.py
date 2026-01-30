"""
003 - Create historical_prices table for caching
緩存歷史價格數據，減少外部 API 調用
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'historical_prices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(20), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('open', sa.Float(), nullable=False),
        sa.Column('high', sa.Float(), nullable=False),
        sa.Column('low', sa.Float(), nullable=False),
        sa.Column('close', sa.Float(), nullable=False),
        sa.Column('volume', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 創建索引
    op.create_index('ix_historical_prices_id', 'historical_prices', ['id'])
    op.create_index('ix_historical_prices_symbol', 'historical_prices', ['symbol'])
    op.create_index('uq_symbol_date', 'historical_prices', ['symbol', 'date'], unique=True)
    op.create_index('idx_symbol_date_range', 'historical_prices', ['symbol', 'date'])

def downgrade():
    op.drop_index('idx_symbol_date_range', 'historical_prices')
    op.drop_index('uq_symbol_date', 'historical_prices')
    op.drop_index('ix_historical_prices_symbol', 'historical_prices')
    op.drop_index('ix_historical_prices_id', 'historical_prices')
    op.drop_table('historical_prices')
