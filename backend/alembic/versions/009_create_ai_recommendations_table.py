"""create ai recommendations table

Revision ID: 009
Revises: 008
Create Date: 2026-01-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'ai_recommendations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('symbol', sa.String(20), nullable=False),
        sa.Column('stock_name', sa.String(100), nullable=False),
        sa.Column('market', sa.String(10), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('ai_score', sa.Float(), nullable=False),
        sa.Column('recommendation', sa.String(20), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('technical_score', sa.Float(), nullable=False),
        sa.Column('fundamental_score', sa.Float(), nullable=False),
        sa.Column('sentiment_score', sa.Float(), nullable=False),
        sa.Column('reasons', JSON, nullable=False),
        sa.Column('technical_indicators', JSON, nullable=True),
        sa.Column('fundamental_data', JSON, nullable=True),
        sa.Column('news_sentiment', sa.String(20), nullable=True),
        sa.Column('latest_news', JSON, nullable=True),
        sa.Column('price_after_7d', sa.Float(), nullable=True),
        sa.Column('price_after_30d', sa.Float(), nullable=True),
        sa.Column('return_7d', sa.Float(), nullable=True),
        sa.Column('return_30d', sa.Float(), nullable=True),
        sa.Column('accuracy_label', sa.String(20), nullable=True),
        sa.Column('recommended_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # 建立索引
    op.create_index('idx_symbol_recommended_at', 'ai_recommendations', ['symbol', 'recommended_at'])
    op.create_index('idx_recommendation', 'ai_recommendations', ['recommendation'])
    op.create_index('idx_ai_score', 'ai_recommendations', ['ai_score'])
    op.create_index('idx_market', 'ai_recommendations', ['market'])
    op.create_index('idx_ai_rec_symbol', 'ai_recommendations', ['symbol'])
    op.create_index('idx_ai_rec_recommended_at', 'ai_recommendations', ['recommended_at'])


def downgrade():
    op.drop_index('idx_ai_rec_recommended_at', 'ai_recommendations')
    op.drop_index('idx_ai_rec_symbol', 'ai_recommendations')
    op.drop_index('idx_market', 'ai_recommendations')
    op.drop_index('idx_ai_score', 'ai_recommendations')
    op.drop_index('idx_recommendation', 'ai_recommendations')
    op.drop_index('idx_symbol_recommended_at', 'ai_recommendations')
    op.drop_table('ai_recommendations')
