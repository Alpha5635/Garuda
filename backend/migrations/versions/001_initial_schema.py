"""initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-22 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Organisations
    op.create_table(
        'organisations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=100), nullable=True),
        sa.Column('brand', sa.String(length=255), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # 2. Users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='officer'),
        sa.Column('organisation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organisations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 3. Inspections
    op.create_table(
        'inspections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('inspection_number', sa.String(length=100), nullable=False, unique=True),
        sa.Column('officer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('organisation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organisations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('channel', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('district', sa.String(length=100), nullable=True),
        sa.Column('product_name', sa.String(length=255), nullable=True),
        sa.Column('brand_name', sa.String(length=255), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_inspections_inspection_number'), 'inspections', ['inspection_number'], unique=True)

    # 4. Images
    op.create_table(
        'images',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('inspection_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('object_key', sa.String(length=500), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=True),
        sa.Column('sha256_hash', sa.String(length=64), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('capture_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('gps_latitude', sa.Float(), nullable=True),
        sa.Column('gps_longitude', sa.Float(), nullable=True),
        sa.Column('exif_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_images_sha256_hash'), 'images', ['sha256_hash'], unique=False)

    # 5. Processing Jobs
    op.create_table(
        'processing_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('inspection_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('image_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('images.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='queued'),
        sa.Column('error_reason', sa.String(length=255), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('quality_metrics_json', sa.JSON(), nullable=True),
        sa.Column('ocr_data_json', sa.JSON(), nullable=True),
        sa.Column('extracted_fields_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('processing_jobs')
    op.drop_index(op.f('ix_images_sha256_hash'), table_name='images')
    op.drop_table('images')
    op.drop_index(op.f('ix_inspections_inspection_number'), table_name='inspections')
    op.drop_table('inspections')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('organisations')
