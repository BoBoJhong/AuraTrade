"""Create positions table

Revision ID: 005
Revises: 004
Create Date: 2026-01-30 14:46:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create positions table
    op.create_table(
        'positions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False, comment='持有數量'),
        sa.Column('buy_price', sa.Float(), nullable=False, comment='買入均價'),
        sa.Column('buy_date', sa.DateTime(), nullable=False, comment='買入日期'),
        sa.Column('notes', sa.String(length=500), nullable=True, comment='備註'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['symbol'], ['stocks.symbol'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_positions_id'), 'positions', ['id'], unique=False)
    op.create_index('ix_positions_user_id', 'positions', ['user_id'], unique=False)
    op.create_index('ix_positions_symbol', 'positions', ['symbol'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_positions_symbol', table_name='positions')
    op.drop_index('ix_positions_user_id', table_name='positions')
    op.drop_index(op.f('ix_positions_id'), table_name='positions')
    op.drop_table('positions')
