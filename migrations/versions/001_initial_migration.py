"""Initial migration - create sar_records table

Revision ID: 001
Revises: 
Create Date: 2024-01-29

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
    """Create sar_records table with indexes."""
    op.create_table(
        'sar_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('request_id', sa.String(length=64), nullable=False),
        sa.Column('submitter_identity', sa.String(length=255), nullable=False),
        sa.Column('submitted_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('client_ip', postgresql.INET(), nullable=True),
        sa.Column('sar_xml', sa.Text(), nullable=False),
        sa.Column('normalized_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('idempotency_key', sa.String(length=128), nullable=True),
        sa.Column('validation_status', sa.String(length=20), nullable=False, server_default='valid'),
        sa.Column('validation_errors', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('request_id'),
        sa.UniqueConstraint('idempotency_key')
    )
    
    # Create indexes
    op.create_index('idx_sar_records_submitted_at', 'sar_records', ['submitted_at'])
    op.create_index('idx_sar_records_submitter', 'sar_records', ['submitter_identity'])
    op.create_index(
        'idx_sar_records_idempotency',
        'sar_records',
        ['idempotency_key'],
        postgresql_where=sa.text('idempotency_key IS NOT NULL')
    )


def downgrade() -> None:
    """Drop sar_records table and indexes."""
    op.drop_index('idx_sar_records_idempotency', table_name='sar_records')
    op.drop_index('idx_sar_records_submitter', table_name='sar_records')
    op.drop_index('idx_sar_records_submitted_at', table_name='sar_records')
    op.drop_table('sar_records')
