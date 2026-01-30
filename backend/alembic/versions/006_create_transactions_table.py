"""Create transactions table

Revision ID: 006
Revises: 005
Create Date: 2026-01-30 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stock_symbol', sa.String(length=20), nullable=False),
        sa.Column('transaction_type', sa.String(length=10), nullable=False, comment='buy or sell'),
        sa.Column('quantity', sa.Float(), nullable=False, comment='交易股數'),
        sa.Column('price', sa.Float(), nullable=False, comment='成交價格'),
        sa.Column('commission', sa.Float(), nullable=True, default=0, comment='手續費'),
        sa.Column('tax', sa.Float(), nullable=True, default=0, comment='交易稅'),
        sa.Column('total_amount', sa.Float(), nullable=False, comment='總金額 (包含手續費和稅)'),
        sa.Column('transaction_date', sa.Date(), nullable=False, comment='交易日期'),
        sa.Column('notes', sa.String(length=500), nullable=True, comment='備註'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['stock_symbol'], ['stocks.symbol'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)
    op.create_index('ix_transactions_user_id', 'transactions', ['user_id'], unique=False)
    op.create_index('ix_transactions_stock_symbol', 'transactions', ['stock_symbol'], unique=False)
    op.create_index('ix_transactions_date', 'transactions', ['transaction_date'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_transactions_date', table_name='transactions')
    op.drop_index('ix_transactions_stock_symbol', table_name='transactions')
    op.drop_index('ix_transactions_user_id', table_name='transactions')
    op.drop_index(op.f('ix_transactions_id'), table_name='transactions')
    op.drop_table('transactions')
