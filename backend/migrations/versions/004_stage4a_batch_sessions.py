"""stage4a batch inspection sessions and product detections

Revision ID: 004_stage4a_batch_sessions
Revises: 003_stage3_tables
Create Date: 2026-08-23 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004_stage4a_batch_sessions'
down_revision: Union[str, None] = '003_stage3_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Inspection Sessions
    op.create_table(
        'inspection_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organisation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organisations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('inspector_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('client_session_id', sa.String(length=100), nullable=True),
        sa.Column('idempotency_key', sa.String(length=100), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('gps_accuracy', sa.Float(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='queued'),
        sa.Column('total_images', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_products', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('processed_products', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_inspection_sessions_organisation_id'), 'inspection_sessions', ['organisation_id'], unique=False)
    op.create_index(op.f('ix_inspection_sessions_inspector_id'), 'inspection_sessions', ['inspector_id'], unique=False)
    op.create_index(op.f('ix_inspection_sessions_client_session_id'), 'inspection_sessions', ['client_session_id'], unique=False)
    op.create_index(op.f('ix_inspection_sessions_idempotency_key'), 'inspection_sessions', ['idempotency_key'], unique=True)

    # 2. Product Detections
    op.create_table(
        'product_detections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('inspection_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('image_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('images.id', ondelete='CASCADE'), nullable=False),
        sa.Column('bbox_x', sa.Float(), nullable=False),
        sa.Column('bbox_y', sa.Float(), nullable=False),
        sa.Column('bbox_width', sa.Float(), nullable=False),
        sa.Column('bbox_height', sa.Float(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('crop_object_key', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='detected'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_product_detections_session_id'), 'product_detections', ['session_id'], unique=False)
    op.create_index(op.f('ix_product_detections_image_id'), 'product_detections', ['image_id'], unique=False)

    # 3. Alter Images table
    op.alter_column('images', 'inspection_id', existing_type=postgresql.UUID(as_uuid=True), nullable=True)
    op.add_column('images', sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('inspection_sessions.id', ondelete='CASCADE'), nullable=True))
    op.create_index(op.f('ix_images_session_id'), 'images', ['session_id'], unique=False)

    # 4. Alter Inspections table
    op.add_column('inspections', sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('inspection_sessions.id', ondelete='SET NULL'), nullable=True))
    op.add_column('inspections', sa.Column('detection_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('product_detections.id', ondelete='SET NULL'), nullable=True))
    op.add_column('inspections', sa.Column('idempotency_key', sa.String(length=100), nullable=True))
    op.add_column('inspections', sa.Column('client_inspection_id', sa.String(length=100), nullable=True))
    op.create_index(op.f('ix_inspections_session_id'), 'inspections', ['session_id'], unique=False)
    op.create_index(op.f('ix_inspections_detection_id'), 'inspections', ['detection_id'], unique=False)
    op.create_index(op.f('ix_inspections_idempotency_key'), 'inspections', ['idempotency_key'], unique=True)
    op.create_index(op.f('ix_inspections_client_inspection_id'), 'inspections', ['client_inspection_id'], unique=False)


def downgrade() -> None:
    # 4. Downgrade Inspections
    op.drop_index(op.f('ix_inspections_client_inspection_id'), table_name='inspections')
    op.drop_index(op.f('ix_inspections_idempotency_key'), table_name='inspections')
    op.drop_index(op.f('ix_inspections_detection_id'), table_name='inspections')
    op.drop_index(op.f('ix_inspections_session_id'), table_name='inspections')
    op.drop_column('inspections', 'client_inspection_id')
    op.drop_column('inspections', 'idempotency_key')
    op.drop_column('inspections', 'detection_id')
    op.drop_column('inspections', 'session_id')

    # 3. Downgrade Images
    op.drop_index(op.f('ix_images_session_id'), table_name='images')
    op.drop_column('images', 'session_id')
    op.alter_column('images', 'inspection_id', existing_type=postgresql.UUID(as_uuid=True), nullable=False)

    # 2. Downgrade Product Detections
    op.drop_index(op.f('ix_product_detections_image_id'), table_name='product_detections')
    op.drop_index(op.f('ix_product_detections_session_id'), table_name='product_detections')
    op.drop_table('product_detections')

    # 1. Downgrade Inspection Sessions
    op.drop_index(op.f('ix_inspection_sessions_idempotency_key'), table_name='inspection_sessions')
    op.drop_index(op.f('ix_inspection_sessions_client_session_id'), table_name='inspection_sessions')
    op.drop_index(op.f('ix_inspection_sessions_inspector_id'), table_name='inspection_sessions')
    op.drop_index(op.f('ix_inspection_sessions_organisation_id'), table_name='inspection_sessions')
    op.drop_table('inspection_sessions')
