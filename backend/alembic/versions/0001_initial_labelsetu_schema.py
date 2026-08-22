"""Initial LabelSetu 19-table schema migration with PostGIS, pg_trgm, and FTS.

Revision ID: 0001_initial_labelsetu_schema
Revises: 
Create Date: 2026-08-22 13:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geography

# revision identifiers, used by Alembic.
revision: str = '0001_initial_labelsetu_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    # 1. Create PostgreSQL Extensions if applicable
    if is_postgres:
        op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    # 2. Table: organisations
    op.create_table(
        'organisations',
        sa.Column('id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('state_code', sa.String(length=10), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_organisations_name', 'organisations', ['name'])
    op.create_index('ix_organisations_type', 'organisations', ['type'])
    op.create_index('ix_organisations_state_code', 'organisations', ['state_code'])
    op.create_index('ix_organisations_status', 'organisations', ['status'])
    op.create_index('ix_organisations_type_state', 'organisations', ['type', 'state_code'])

    # 3. Table: roles
    op.create_table(
        'roles',
        sa.Column('id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), primary_key=True),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('permissions_jsonb', postgresql.JSONB(astext_type=sa.Text()) if is_postgres else sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.UniqueConstraint('code', name='uq_roles_code'),
    )
    op.create_index('ix_roles_code', 'roles', ['code'])

    # 4. Table: users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), primary_key=True),
        sa.Column('organisation_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('organisations.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.UniqueConstraint('email', name='uq_users_email'),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_organisation_id', 'users', ['organisation_id'])
    op.create_index('ix_users_status', 'users', ['status'])

    # 5. Table: user_roles
    op.create_table(
        'user_roles',
        sa.Column('id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('organisation_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('organisations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.UniqueConstraint('user_id', 'role_id', 'organisation_id', name='uq_user_role_org'),
    )
    op.create_index('ix_user_roles_user_id', 'user_roles', ['user_id'])
    op.create_index('ix_user_roles_role_id', 'user_roles', ['role_id'])
    op.create_index('ix_user_roles_organisation_id', 'user_roles', ['organisation_id'])

    # 6. Table: brands
    op.create_table(
        'brands',
        sa.Column('id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), primary_key=True),
        sa.Column('canonical_name', sa.String(length=255), nullable=False),
        sa.Column('aliases_jsonb', postgresql.JSONB(astext_type=sa.Text()) if is_postgres else sa.JSON(), nullable=False),
        sa.Column('manufacturer_org_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('organisations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_brands_canonical_name', 'brands', ['canonical_name'])
    op.create_index('ix_brands_manufacturer_org_id', 'brands', ['manufacturer_org_id'])
    if is_postgres:
        op.execute("CREATE INDEX IF NOT EXISTS ix_brands_canonical_name_trgm ON brands USING gin (canonical_name gin_trgm_ops);")

    # 7. Table: products
    op.create_table(
        'products',
        sa.Column('id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), primary_key=True),
        sa.Column('brand_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('brands.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('generic_name', sa.String(length=255), nullable=False),
        sa.Column('sku', sa.String(length=100), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('is_imported', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('metadata_jsonb', postgresql.JSONB(astext_type=sa.Text()) if is_postgres else sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_products_brand_id', 'products', ['brand_id'])
    op.create_index('ix_products_generic_name', 'products', ['generic_name'])
    op.create_index('ix_products_sku', 'products', ['sku'])
    op.create_index('ix_products_category', 'products', ['category'])
    op.create_index('ix_products_category_imported', 'products', ['category', 'is_imported'])

    # 8. Table: rule_packs
    op.create_table(
        'rule_packs',
        sa.Column('id', sa.String(length=100), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('jurisdiction', sa.String(length=100), nullable=False, server_default='India'),
        sa.Column('owner_org_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('organisations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_rule_packs_owner_org_id', 'rule_packs', ['owner_org_id'])

    # 9. Table: rule_versions
    op.create_table(
        'rule_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), primary_key=True),
        sa.Column('rule_pack_id', sa.String(length=100), sa.ForeignKey('rule_packs.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('effective_from', sa.DateTime(timezone=True), nullable=False),
        sa.Column('content_jsonb', postgresql.JSONB(astext_type=sa.Text()) if is_postgres else sa.JSON(), nullable=False),
        sa.Column('sha256', sa.String(length=64), nullable=False),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='staged'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.UniqueConstraint('rule_pack_id', 'version', name='uq_rule_pack_version'),
    )
    op.create_index('ix_rule_versions_rule_pack_id', 'rule_versions', ['rule_pack_id'])
    op.create_index('ix_rule_versions_version', 'rule_versions', ['version'])
    op.create_index('ix_rule_versions_status', 'rule_versions', ['status'])
    op.create_index('ix_rule_versions_status_effective', 'rule_versions', ['status', 'effective_from'])

    # 10. Table: model_versions
    op.create_table(
        'model_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('artifact_uri', sa.String(length=500), nullable=False),
        sa.Column('metrics_jsonb', postgresql.JSONB(astext_type=sa.Text()) if is_postgres else sa.JSON(), nullable=False),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.UniqueConstraint('name', 'version', name='uq_model_name_version'),
    )
    op.create_index('ix_model_versions_name', 'model_versions', ['name'])
    op.create_index('ix_model_versions_version', 'model_versions', ['version'])

    # 11. Table: inspections
    op.create_table(
        'inspections',
        sa.Column('id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), primary_key=True),
        sa.Column('organisation_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('organisations.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('products.id', ondelete='SET NULL'), nullable=True),
        sa.Column('channel', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('rule_version_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('rule_versions.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('score_status', sa.String(length=50), nullable=True, server_default='provisional'),
        sa.Column('location', Geography(geometry_type='POINT', srid=4326) if is_postgres else sa.String(100), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('district', sa.String(length=100), nullable=True),
        sa.Column('state_code', sa.String(length=10), nullable=True),
        sa.Column('officer_notes', sa.Text(), nullable=True),
        sa.Column('search_vector', postgresql.TSVECTOR() if is_postgres else sa.Text(), nullable=True),
        sa.Column('captured_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_inspections_organisation_id', 'inspections', ['organisation_id'])
    op.create_index('ix_inspections_product_id', 'inspections', ['product_id'])
    op.create_index('ix_inspections_channel', 'inspections', ['channel'])
    op.create_index('ix_inspections_status', 'inspections', ['status'])
    op.create_index('ix_inspections_rule_version_id', 'inspections', ['rule_version_id'])
    op.create_index('ix_inspections_district', 'inspections', ['district'])
    op.create_index('ix_inspections_state_code', 'inspections', ['state_code'])
    op.create_index('ix_inspections_captured_at', 'inspections', ['captured_at'])
    op.create_index('ix_inspections_created_by', 'inspections', ['created_by'])
    op.create_index('ix_inspections_org_status_channel', 'inspections', ['organisation_id', 'status', 'channel'])
    op.create_index('ix_inspections_district_captured', 'inspections', ['district', 'captured_at'])
    if is_postgres:
        op.execute("CREATE INDEX IF NOT EXISTS ix_inspections_search_vector ON inspections USING gin (search_vector);")

    # 12. Table: product_images
    op.create_table(
        'product_images',
        sa.Column('id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), primary_key=True),
        sa.Column('inspection_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('object_key', sa.String(length=500), nullable=False),
        sa.Column('sha256', sa.String(length=64), nullable=False),
        sa.Column('captured_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('location', Geography(geometry_type='POINT', srid=4326) if is_postgres else sa.String(100), nullable=True),
        sa.Column('gps_accuracy_m', sa.Float(), nullable=True),
        sa.Column('quality_jsonb', postgresql.JSONB(astext_type=sa.Text()) if is_postgres else sa.JSON(), nullable=False),
        sa.Column('transform_jsonb', postgresql.JSONB(astext_type=sa.Text()) if is_postgres else sa.JSON(), nullable=False),
        sa.Column('calibration_jsonb', postgresql.JSONB(astext_type=sa.Text()) if is_postgres else sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='uploaded'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_product_images_inspection_id', 'product_images', ['inspection_id'])
    op.create_index('ix_product_images_sha256', 'product_images', ['sha256'])
    op.create_index('ix_product_images_status', 'product_images', ['status'])

    # 13. Table: extracted_fields
    op.create_table(
        'extracted_fields',
        sa.Column('id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), primary_key=True),
        sa.Column('inspection_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('image_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('product_images.id', ondelete='SET NULL'), nullable=True),
        sa.Column('field_type', sa.String(length=100), nullable=False),
        sa.Column('raw_text', sa.Text(), nullable=False),
        sa.Column('normalized_jsonb', postgresql.JSONB(astext_type=sa.Text()) if is_postgres else sa.JSON(), nullable=False),
        sa.Column('bbox_jsonb', postgresql.JSONB(astext_type=sa.Text()) if is_postgres else sa.JSON(), nullable=False),
        sa.Column('polygon_jsonb', postgresql.JSONB(astext_type=sa.Text()) if is_postgres else sa.JSON(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('language', sa.String(length=20), nullable=False, server_default='eng'),
        sa.Column('model_version', sa.String(length=100), nullable=True),
        sa.Column('model_version_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('model_versions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('review_status', sa.String(length=50), nullable=False, server_default='unreviewed'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_extracted_fields_inspection_id', 'extracted_fields', ['inspection_id'])
    op.create_index('ix_extracted_fields_image_id', 'extracted_fields', ['image_id'])
    op.create_index('ix_extracted_fields_field_type', 'extracted_fields', ['field_type'])
    op.create_index('ix_extracted_fields_review_status', 'extracted_fields', ['review_status'])
    op.create_index('ix_extracted_fields_inspection_type', 'extracted_fields', ['inspection_id', 'field_type'])

    # 14. Table: violations
    op.create_table(
        'violations',
        sa.Column('id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), primary_key=True),
        sa.Column('inspection_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rule_version_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('rule_versions.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('rule_id', sa.String(length=100), nullable=False),
        sa.Column('clause', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='detected'),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('evidence_jsonb', postgresql.JSONB(astext_type=sa.Text()) if is_postgres else sa.JSON(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('officer_disposition', sa.String(length=50), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_violations_inspection_id', 'violations', ['inspection_id'])
    op.create_index('ix_violations_rule_version_id', 'violations', ['rule_version_id'])
    op.create_index('ix_violations_rule_id', 'violations', ['rule_id'])
    op.create_index('ix_violations_status', 'violations', ['status'])
    op.create_index('ix_violations_severity', 'violations', ['severity'])
    op.create_index('ix_violations_severity_status', 'violations', ['severity', 'status'])

    # 15. Table: reports
    op.create_table(
        'reports',
        sa.Column('id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), primary_key=True),
        sa.Column('inspection_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False, server_default='1.0'),
        sa.Column('object_key', sa.String(length=500), nullable=False),
        sa.Column('sha256', sa.String(length=64), nullable=False),
        sa.Column('generated_by', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_reports_inspection_id', 'reports', ['inspection_id'])
    op.create_index('ix_reports_type', 'reports', ['type'])
    op.create_index('ix_reports_sha256', 'reports', ['sha256'])

    # 16. Table: review_actions
    op.create_table(
        'review_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), primary_key=True),
        sa.Column('inspection_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('field_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('extracted_fields.id', ondelete='SET NULL'), nullable=True),
        sa.Column('violation_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('violations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('corrected_value_jsonb', postgresql.JSONB(astext_type=sa.Text()) if is_postgres else sa.JSON(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_review_actions_inspection_id', 'review_actions', ['inspection_id'])
    op.create_index('ix_review_actions_field_id', 'review_actions', ['field_id'])
    op.create_index('ix_review_actions_violation_id', 'review_actions', ['violation_id'])
    op.create_index('ix_review_actions_reviewer_id', 'review_actions', ['reviewer_id'])
    op.create_index('ix_review_actions_action', 'review_actions', ['action'])

    # 17. Table: audit_log
    op.create_table(
        'audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), primary_key=True),
        sa.Column('organisation_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('organisations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.String(length=100), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('before_jsonb', postgresql.JSONB(astext_type=sa.Text()) if is_postgres else sa.JSON(), nullable=True),
        sa.Column('after_jsonb', postgresql.JSONB(astext_type=sa.Text()) if is_postgres else sa.JSON(), nullable=True),
        sa.Column('event_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('prev_hash', sa.String(length=64), nullable=True),
        sa.Column('event_hash', sa.String(length=64), nullable=False),
        sa.Column('request_id', sa.String(length=100), nullable=True),
        sa.UniqueConstraint('event_hash', name='uq_audit_log_event_hash'),
    )
    op.create_index('ix_audit_log_organisation_id', 'audit_log', ['organisation_id'])
    op.create_index('ix_audit_log_actor_id', 'audit_log', ['actor_id'])
    op.create_index('ix_audit_log_entity_type', 'audit_log', ['entity_type'])
    op.create_index('ix_audit_log_entity_id', 'audit_log', ['entity_id'])
    op.create_index('ix_audit_log_action', 'audit_log', ['action'])
    op.create_index('ix_audit_log_event_at', 'audit_log', ['event_at'])
    op.create_index('ix_audit_log_event_hash', 'audit_log', ['event_hash'])
    op.create_index('ix_audit_log_entity_lookup', 'audit_log', ['entity_type', 'entity_id'])
    op.create_index('ix_audit_log_actor_time', 'audit_log', ['actor_id', 'event_at'])

    # 18. Table: offenders
    op.create_table(
        'offenders',
        sa.Column('id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), primary_key=True),
        sa.Column('brand_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('brands.id', ondelete='CASCADE'), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('inspection_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('confirmed_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('severity_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_offenders_brand_id', 'offenders', ['brand_id'])
    op.create_index('ix_offenders_period_start', 'offenders', ['period_start'])
    op.create_index('ix_offenders_period_end', 'offenders', ['period_end'])
    op.create_index('ix_offenders_brand_period', 'offenders', ['brand_id', 'period_start', 'period_end'])

    # 19. Table: sync_queue
    op.create_table(
        'sync_queue',
        sa.Column('id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), primary_key=True),
        sa.Column('device_id', sa.String(length=100), nullable=False),
        sa.Column('local_event_id', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('payload_jsonb', postgresql.JSONB(astext_type=sa.Text()) if is_postgres else sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('idempotency_key', sa.String(length=255), nullable=False),
        sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.UniqueConstraint('idempotency_key', name='uq_sync_queue_idempotency_key'),
    )
    op.create_index('ix_sync_queue_device_id', 'sync_queue', ['device_id'])
    op.create_index('ix_sync_queue_status', 'sync_queue', ['status'])
    op.create_index('ix_sync_queue_idempotency_key', 'sync_queue', ['idempotency_key'])
    op.create_index('ix_sync_queue_device_status', 'sync_queue', ['device_id', 'status'])

    # 20. Table: ecommerce_listings
    op.create_table(
        'ecommerce_listings',
        sa.Column('id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), primary_key=True),
        sa.Column('platform', sa.String(length=100), nullable=False),
        sa.Column('external_listing_id', sa.String(length=255), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True) if is_postgres else sa.CHAR(36), sa.ForeignKey('products.id', ondelete='SET NULL'), nullable=True),
        sa.Column('snapshot_key', sa.String(length=500), nullable=True),
        sa.Column('content_hash', sa.String(length=64), nullable=True),
        sa.Column('captured_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('seller_name', sa.String(length=255), nullable=True),
        sa.Column('availability', sa.String(length=50), nullable=True),
        sa.Column('raw_jsonb', postgresql.JSONB(astext_type=sa.Text()) if is_postgres else sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.UniqueConstraint('platform', 'external_listing_id', name='uq_platform_external_listing'),
    )
    op.create_index('ix_ecommerce_listings_platform', 'ecommerce_listings', ['platform'])
    op.create_index('ix_ecommerce_listings_external_id', 'ecommerce_listings', ['external_listing_id'])
    op.create_index('ix_ecommerce_listings_product_id', 'ecommerce_listings', ['product_id'])
    op.create_index('ix_ecommerce_listings_seller_name', 'ecommerce_listings', ['seller_name'])
    op.create_index('ix_ecommerce_platform_seller', 'ecommerce_listings', ['platform', 'seller_name'])


def downgrade() -> None:
    op.drop_table('ecommerce_listings')
    op.drop_table('sync_queue')
    op.drop_table('offenders')
    op.drop_table('audit_log')
    op.drop_table('review_actions')
    op.drop_table('reports')
    op.drop_table('violations')
    op.drop_table('extracted_fields')
    op.drop_table('product_images')
    op.drop_table('inspections')
    op.drop_table('model_versions')
    op.drop_table('rule_versions')
    op.drop_table('rule_packs')
    op.drop_table('products')
    op.drop_table('brands')
    op.drop_table('user_roles')
    op.drop_table('users')
    op.drop_table('roles')
    op.drop_table('organisations')
