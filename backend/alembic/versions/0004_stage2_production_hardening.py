"""Stage 2: Production Hardening, Audit, Search, and Intelligence schema extensions.

Revision ID: 0004_stage2_production_hardening
Revises: 0003_batch_inspection_foundation
Create Date: 2026-08-23 15:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0004_stage2_production_hardening'
down_revision: Union[str, None] = '0003_batch_inspection_foundation'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Review Actions
    op.add_column(
        'review_actions',
        sa.Column('original_value_jsonb', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )

    # 2. Offenders
    op.add_column('offenders', sa.Column('organisation_id', sa.UUID(), nullable=True))
    op.add_column('offenders', sa.Column('product_id', sa.UUID(), nullable=True))
    op.create_foreign_key('fk_offenders_org_id', 'offenders', 'organisations', ['organisation_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_offenders_prod_id', 'offenders', 'products', ['product_id'], ['id'], ondelete='SET NULL')
    op.create_index('ix_offenders_org_brand', 'offenders', ['organisation_id', 'brand_id'])

    # 3. Ecommerce Listings
    op.add_column('ecommerce_listings', sa.Column('organisation_id', sa.UUID(), nullable=True))
    op.add_column('ecommerce_listings', sa.Column('listing_id', sa.String(length=255), nullable=True))
    op.add_column('ecommerce_listings', sa.Column('title', sa.String(length=500), nullable=True))
    op.add_column('ecommerce_listings', sa.Column('seller', sa.String(length=255), nullable=True))
    op.add_column('ecommerce_listings', sa.Column('snapshot_object_key', sa.String(length=500), nullable=True))
    op.add_column('ecommerce_listings', sa.Column('raw_payload_jsonb', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'))
    op.create_foreign_key('fk_ecommerce_org_id', 'ecommerce_listings', 'organisations', ['organisation_id'], ['id'], ondelete='SET NULL')
    op.create_index('ix_ecommerce_listing_id', 'ecommerce_listings', ['listing_id'])
    op.create_index('ix_ecommerce_seller', 'ecommerce_listings', ['seller'])
    op.create_index('ix_ecommerce_org_platform', 'ecommerce_listings', ['organisation_id', 'platform'])

    # 4. Model Versions
    op.add_column('model_versions', sa.Column('task', sa.String(length=100), nullable=True, server_default='ocr'))
    op.add_column('model_versions', sa.Column('released_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index('ix_model_versions_task', 'model_versions', ['task'])

    # 5. Sync Queue
    op.add_column('sync_queue', sa.Column('organisation_id', sa.UUID(), nullable=True))
    op.add_column('sync_queue', sa.Column('client_id', sa.String(length=100), nullable=True))
    op.add_column('sync_queue', sa.Column('entity_id', sa.String(length=100), nullable=True))
    op.add_column('sync_queue', sa.Column('payload_hash', sa.String(length=64), nullable=True))
    op.add_column('sync_queue', sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('sync_queue', sa.Column('last_error', sa.Text(), nullable=True))
    op.create_foreign_key('fk_sync_queue_org_id', 'sync_queue', 'organisations', ['organisation_id'], ['id'], ondelete='CASCADE')
    op.create_index('ix_sync_queue_client_id', 'sync_queue', ['client_id'])
    op.create_index('ix_sync_queue_entity_id', 'sync_queue', ['entity_id'])
    op.create_index('ix_sync_queue_org_status', 'sync_queue', ['organisation_id', 'status'])


def downgrade() -> None:
    # 5. Sync Queue
    op.drop_constraint('fk_sync_queue_org_id', 'sync_queue', type_='foreignkey')
    op.drop_index('ix_sync_queue_org_status', table_name='sync_queue')
    op.drop_index('ix_sync_queue_entity_id', table_name='sync_queue')
    op.drop_index('ix_sync_queue_client_id', table_name='sync_queue')
    op.drop_column('sync_queue', 'last_error')
    op.drop_column('sync_queue', 'retry_count')
    op.drop_column('sync_queue', 'payload_hash')
    op.drop_column('sync_queue', 'entity_id')
    op.drop_column('sync_queue', 'client_id')
    op.drop_column('sync_queue', 'organisation_id')

    # 4. Model Versions
    op.drop_index('ix_model_versions_task', table_name='model_versions')
    op.drop_column('model_versions', 'released_at')
    op.drop_column('model_versions', 'task')

    # 3. Ecommerce Listings
    op.drop_constraint('fk_ecommerce_org_id', 'ecommerce_listings', type_='foreignkey')
    op.drop_index('ix_ecommerce_org_platform', table_name='ecommerce_listings')
    op.drop_index('ix_ecommerce_seller', table_name='ecommerce_listings')
    op.drop_index('ix_ecommerce_listing_id', table_name='ecommerce_listings')
    op.drop_column('ecommerce_listings', 'raw_payload_jsonb')
    op.drop_column('ecommerce_listings', 'snapshot_object_key')
    op.drop_column('ecommerce_listings', 'seller')
    op.drop_column('ecommerce_listings', 'title')
    op.drop_column('ecommerce_listings', 'listing_id')
    op.drop_column('ecommerce_listings', 'organisation_id')

    # 2. Offenders
    op.drop_constraint('fk_offenders_prod_id', 'offenders', type_='foreignkey')
    op.drop_constraint('fk_offenders_org_id', 'offenders', type_='foreignkey')
    op.drop_index('ix_offenders_org_brand', table_name='offenders')
    op.drop_column('offenders', 'product_id')
    op.drop_column('offenders', 'organisation_id')

    # 1. Review Actions
    op.drop_column('review_actions', 'original_value_jsonb')
