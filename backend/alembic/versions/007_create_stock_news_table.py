"""create stock news table

Revision ID: 007
Revises: 006
Create Date: 2026-01-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    # Create stock_news table
    op.create_table(
        'stock_news',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('url', sa.String(length=1000), nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sentiment', sa.String(length=20), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_stock_news_id', 'stock_news', ['id'])
    op.create_index('ix_stock_news_symbol', 'stock_news', ['symbol'])
    op.create_index('ix_stock_news_published_at', 'stock_news', ['published_at'])
    op.create_index('idx_symbol_published', 'stock_news', ['symbol', 'published_at'])
    op.create_index('idx_published_at', 'stock_news', ['published_at'])
    
    # Create unique constraint on URL
    op.create_unique_constraint('uq_stock_news_url', 'stock_news', ['url'])


def downgrade():
    op.drop_table('stock_news')