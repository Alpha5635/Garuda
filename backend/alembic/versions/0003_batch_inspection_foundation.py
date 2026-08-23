"""Add inspection sessions, batch images, product detections, and Stage 1 columns.

Revision ID: 0003_batch_inspection_foundation
Revises: 0002_add_fts_trigger
Create Date: 2026-08-23 15:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0003_batch_inspection_foundation'
down_revision: Union[str, None] = '0002_add_fts_trigger'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add new columns to organisations
    op.add_column('organisations', sa.Column('code', sa.String(length=50), nullable=True))
    op.create_index('ix_organisations_code', 'organisations', ['code'], unique=True)

    # 2. Add new columns to roles
    op.add_column('roles', sa.Column('name', sa.String(length=50), nullable=True))
    op.create_index('ix_roles_name', 'roles', ['name'])

    # 3. Add new columns to users
    op.add_column('users', sa.Column('name', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False))
    op.create_index('ix_users_is_active', 'users', ['is_active'])

    # 4. Add new columns to brands
    op.add_column('brands', sa.Column('name', sa.String(length=255), nullable=True))
    op.add_column('brands', sa.Column('normalized_name', sa.String(length=255), nullable=True))
    op.add_column('brands', sa.Column('organisation_id', sa.UUID(), nullable=True))
    op.create_foreign_key(
        'fk_brands_organisation_id',
        'brands', 'organisations',
        ['organisation_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_brands_normalized_name', 'brands', ['normalized_name'])
    op.create_index('ix_brands_organisation_id', 'brands', ['organisation_id'])

    # 5. Add new columns to products
    op.add_column('products', sa.Column('name', sa.String(length=255), nullable=True))
    op.create_index('ix_products_name', 'products', ['name'])

    # 6. Create inspection_sessions table
    op.create_table(
        'inspection_sessions',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('organisation_id', sa.UUID(), nullable=False),
        sa.Column('client_session_id', sa.String(length=100), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('channel', sa.String(length=50), nullable=False, server_default='package'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lon', sa.Float(), nullable=True),
        sa.Column('gps_accuracy_m', sa.Float(), nullable=True),
        sa.Column('captured_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('idempotency_key', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_inspection_sessions_org_id', 'inspection_sessions', ['organisation_id'])
    op.create_index('ix_inspection_sessions_client_session_id', 'inspection_sessions', ['client_session_id'])
    op.create_index('ix_inspection_sessions_channel', 'inspection_sessions', ['channel'])
    op.create_index('ix_inspection_sessions_status', 'inspection_sessions', ['status'])
    op.create_index('ix_inspection_sessions_idempotency_key', 'inspection_sessions', ['idempotency_key'], unique=True)
    op.create_index('ix_inspection_sessions_org_status', 'inspection_sessions', ['organisation_id', 'status'])
    op.create_index('ix_inspection_sessions_channel_captured', 'inspection_sessions', ['channel', 'captured_at'])

    # 7. Create batch_images table
    op.create_table(
        'batch_images',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('session_id', sa.UUID(), nullable=False),
        sa.Column('object_key', sa.String(length=500), nullable=False),
        sa.Column('sha256', sa.String(length=64), nullable=False),
        sa.Column('mime_type', sa.String(length=50), nullable=True, server_default='image/jpeg'),
        sa.Column('size_bytes', sa.BigInteger(), nullable=True),
        sa.Column('width_px', sa.Integer(), nullable=True),
        sa.Column('height_px', sa.Integer(), nullable=True),
        sa.Column('captured_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lon', sa.Float(), nullable=True),
        sa.Column('gps_accuracy_m', sa.Float(), nullable=True),
        sa.Column('quality_jsonb', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('transform_jsonb', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('calibration_jsonb', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='uploaded'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['inspection_sessions.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_batch_images_session_id', 'batch_images', ['session_id'])
    op.create_index('ix_batch_images_sha256', 'batch_images', ['sha256'])
    op.create_index('ix_batch_images_status', 'batch_images', ['status'])

    # 8. Create product_detections table
    op.create_table(
        'product_detections',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('batch_image_id', sa.UUID(), nullable=False),
        sa.Column('inspection_id', sa.UUID(), nullable=True),
        sa.Column('detection_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('bbox_jsonb', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('polygon_jsonb', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('crop_object_key', sa.String(length=500), nullable=True),
        sa.Column('detection_confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='detected'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['batch_image_id'], ['batch_images.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_product_detections_batch_image_id', 'product_detections', ['batch_image_id'])
    op.create_index('ix_product_detections_inspection_id', 'product_detections', ['inspection_id'])
    op.create_index('ix_product_detections_status', 'product_detections', ['status'])
    op.create_index('ix_product_detections_batch_status', 'product_detections', ['batch_image_id', 'status'])

    # 9. Add columns and foreign keys to inspections
    op.add_column('inspections', sa.Column('inspection_session_id', sa.UUID(), nullable=True))
    op.add_column('inspections', sa.Column('product_detection_id', sa.UUID(), nullable=True))
    op.add_column('inspections', sa.Column('client_inspection_id', sa.String(length=100), nullable=True))
    op.add_column('inspections', sa.Column('idempotency_key', sa.String(length=255), nullable=True))
    op.add_column('inspections', sa.Column('lat', sa.Float(), nullable=True))
    op.add_column('inspections', sa.Column('lon', sa.Float(), nullable=True))
    op.alter_column('inspections', 'rule_version_id', existing_type=sa.UUID(), nullable=True)

    op.create_foreign_key(
        'fk_inspections_inspection_session_id',
        'inspections', 'inspection_sessions',
        ['inspection_session_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_inspections_product_detection_id',
        'inspections', 'product_detections',
        ['product_detection_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_product_detections_inspection_id',
        'product_detections', 'inspections',
        ['inspection_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_inspections_session_id', 'inspections', ['inspection_session_id'])
    op.create_index('ix_inspections_client_inspection_id', 'inspections', ['client_inspection_id'])
    op.create_index('ix_inspections_idempotency_key', 'inspections', ['idempotency_key'], unique=True)

    # 10. Add columns to product_images
    op.add_column('product_images', sa.Column('mime_type', sa.String(length=50), nullable=True, server_default='image/jpeg'))
    op.add_column('product_images', sa.Column('size_bytes', sa.BigInteger(), nullable=True))
    op.add_column('product_images', sa.Column('width_px', sa.Integer(), nullable=True))
    op.add_column('product_images', sa.Column('height_px', sa.Integer(), nullable=True))
    op.add_column('product_images', sa.Column('lat', sa.Float(), nullable=True))
    op.add_column('product_images', sa.Column('lon', sa.Float(), nullable=True))


def downgrade() -> None:
    # 10. Remove columns from product_images
    op.drop_column('product_images', 'lon')
    op.drop_column('product_images', 'lat')
    op.drop_column('product_images', 'height_px')
    op.drop_column('product_images', 'width_px')
    op.drop_column('product_images', 'size_bytes')
    op.drop_column('product_images', 'mime_type')

    # 9. Remove columns and FKs from inspections
    op.drop_constraint('fk_product_detections_inspection_id', 'product_detections', type_='foreignkey')
    op.drop_constraint('fk_inspections_product_detection_id', 'inspections', type_='foreignkey')
    op.drop_constraint('fk_inspections_inspection_session_id', 'inspections', type_='foreignkey')
    op.drop_index('ix_inspections_idempotency_key', table_name='inspections')
    op.drop_index('ix_inspections_client_inspection_id', table_name='inspections')
    op.drop_index('ix_inspections_session_id', table_name='inspections')
    op.drop_column('inspections', 'lon')
    op.drop_column('inspections', 'lat')
    op.drop_column('inspections', 'idempotency_key')
    op.drop_column('inspections', 'client_inspection_id')
    op.drop_column('inspections', 'product_detection_id')
    op.drop_column('inspections', 'inspection_session_id')

    # 8. Drop product_detections
    op.drop_table('product_detections')

    # 7. Drop batch_images
    op.drop_table('batch_images')

    # 6. Drop inspection_sessions
    op.drop_table('inspection_sessions')

    # 5. Remove name from products
    op.drop_index('ix_products_name', table_name='products')
    op.drop_column('products', 'name')

    # 4. Remove columns from brands
    op.drop_constraint('fk_brands_organisation_id', 'brands', type_='foreignkey')
    op.drop_index('ix_brands_organisation_id', table_name='brands')
    op.drop_index('ix_brands_normalized_name', table_name='brands')
    op.drop_column('brands', 'organisation_id')
    op.drop_column('brands', 'normalized_name')
    op.drop_column('brands', 'name')

    # 3. Remove columns from users
    op.drop_index('ix_users_is_active', table_name='users')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'name')

    # 2. Remove columns from roles
    op.drop_index('ix_roles_name', table_name='roles')
    op.drop_column('roles', 'name')

    # 1. Remove columns from organisations
    op.drop_index('ix_organisations_code', table_name='organisations')
    op.drop_column('organisations', 'code')
