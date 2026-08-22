"""stage2 tables

Revision ID: 002_stage2_tables
Revises: 001_initial_schema
Create Date: 2026-08-22 13:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_stage2_tables'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Normalized Fields
    op.create_table(
        'normalized_fields',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('inspection_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('field_name', sa.String(length=100), nullable=False),
        sa.Column('raw_value', sa.String(length=500), nullable=False),
        sa.Column('normalized_value', sa.String(length=500), nullable=True),
        sa.Column('numeric_value', sa.Float(), nullable=True),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('bounding_box', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_normalized_fields_field_name'), 'normalized_fields', ['field_name'], unique=False)

    # 2. Calibration Data
    op.create_table(
        'calibration_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('inspection_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('image_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('images.id', ondelete='SET NULL'), nullable=True),
        sa.Column('calibration_type', sa.String(length=50), nullable=False),
        sa.Column('reference_width_mm', sa.Float(), nullable=False),
        sa.Column('reference_width_px', sa.Float(), nullable=False),
        sa.Column('pixels_per_mm', sa.Float(), nullable=False),
        sa.Column('measurement_error', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('calibration_confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('perspective_transform', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # 3. Violations
    op.create_table(
        'violations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('inspection_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('image_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('images.id', ondelete='SET NULL'), nullable=True),
        sa.Column('rule_id', sa.String(length=100), nullable=False),
        sa.Column('rule_version', sa.String(length=50), nullable=False),
        sa.Column('clause', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('message', sa.String(length=500), nullable=False),
        sa.Column('evidence_bbox', sa.JSON(), nullable=True),
        sa.Column('evidence_crop_key', sa.String(length=500), nullable=False),
        sa.Column('ocr_text', sa.String(length=500), nullable=True),
        sa.Column('normalized_value', sa.String(length=500), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_violations_rule_id'), 'violations', ['rule_id'], unique=False)

    # 4. Field Corrections
    op.create_table(
        'field_corrections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('inspection_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('field_name', sa.String(length=100), nullable=False),
        sa.Column('original_ocr_value', sa.String(length=500), nullable=True),
        sa.Column('corrected_value', sa.String(length=500), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # 5. Violation Reviews
    op.create_table(
        'violation_reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('violation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('violations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('decision', sa.String(length=50), nullable=False),
        sa.Column('justification_reason', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('violation_reviews')
    op.drop_table('field_corrections')
    op.drop_index(op.f('ix_violations_rule_id'), table_name='violations')
    op.drop_table('violations')
    op.drop_table('calibration_data')
    op.drop_index(op.f('ix_normalized_fields_field_name'), table_name='normalized_fields')
    op.drop_table('normalized_fields')
