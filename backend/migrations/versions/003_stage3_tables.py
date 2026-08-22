"""stage3 tables

Revision ID: 003_stage3_tables
Revises: 002_stage2_tables
Create Date: 2026-08-22 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003_stage3_tables'
down_revision: Union[str, None] = '002_stage2_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Audit Chain
    op.create_table(
        'audit_chain',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('inspection_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=True),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('actor_email', sa.String(length=255), nullable=False, server_default='system'),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.String(length=100), nullable=False),
        sa.Column('before_state', sa.JSON(), nullable=True),
        sa.Column('after_state', sa.JSON(), nullable=True),
        sa.Column('request_id', sa.String(length=100), nullable=True),
        sa.Column('previous_hash', sa.String(length=64), nullable=False),
        sa.Column('current_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_audit_chain_action'), 'audit_chain', ['action'], unique=False)
    op.create_index(op.f('ix_audit_chain_current_hash'), 'audit_chain', ['current_hash'], unique=False)

    # 2. Reports
    op.create_table(
        'reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('inspection_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('format', sa.String(length=20), nullable=False),
        sa.Column('object_key', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('sha256_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_reports_sha256_hash'), 'reports', ['sha256_hash'], unique=False)

    # 3. Ecommerce Listings
    op.create_table(
        'ecommerce_listings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('inspection_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('inspections.id', ondelete='SET NULL'), nullable=True),
        sa.Column('platform', sa.String(length=100), nullable=False),
        sa.Column('listing_id', sa.String(length=100), nullable=False),
        sa.Column('url', sa.String(length=1000), nullable=False),
        sa.Column('seller_name', sa.String(length=255), nullable=True),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('snapshot_key', sa.String(length=500), nullable=True),
        sa.Column('declarations_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_ecommerce_listings_listing_id'), 'ecommerce_listings', ['listing_id'], unique=False)

    # 4. Rule Pack Versions
    op.create_table(
        'rule_pack_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('version', sa.String(length=50), nullable=False, unique=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='staged'),
        sa.Column('rules_json', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_rule_pack_versions_version'), 'rule_pack_versions', ['version'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_rule_pack_versions_version'), table_name='rule_pack_versions')
    op.drop_table('rule_pack_versions')
    op.drop_index(op.f('ix_ecommerce_listings_listing_id'), table_name='ecommerce_listings')
    op.drop_table('ecommerce_listings')
    op.drop_index(op.f('ix_reports_sha256_hash'), table_name='reports')
    op.drop_table('reports')
    op.drop_index(op.f('ix_audit_chain_current_hash'), table_name='audit_chain')
    op.drop_index(op.f('ix_audit_chain_action'), table_name='audit_chain')
    op.drop_table('audit_chain')
