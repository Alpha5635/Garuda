"""Stage 4B batch intelligence, smart recapture, session reports, and audit session link

Revision ID: 005_stage4b_batch_intelligence
Revises: 004_stage4a_batch_sessions
Create Date: 2026-08-23
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '005_stage4b_batch_intelligence'
down_revision: Union[str, None] = '004_stage4a_batch_sessions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update audit_chain table: add session_id
    op.add_column(
        'audit_chain',
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.create_index(
        'ix_audit_chain_session_id',
        'audit_chain',
        ['session_id'],
        unique=False
    )
    op.create_foreign_key(
        'fk_audit_chain_session_id_inspection_sessions',
        'audit_chain',
        'inspection_sessions',
        ['session_id'],
        ['id'],
        ondelete='CASCADE',
        use_alter=True
    )

    # 2. Update reports table: make inspection_id nullable and add session_id
    op.alter_column(
        'reports',
        'inspection_id',
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True
    )
    op.add_column(
        'reports',
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.create_index(
        'ix_reports_session_id',
        'reports',
        ['session_id'],
        unique=False
    )
    op.create_foreign_key(
        'fk_reports_session_id_inspection_sessions',
        'reports',
        'inspection_sessions',
        ['session_id'],
        ['id'],
        ondelete='CASCADE',
        use_alter=True
    )


def downgrade() -> None:
    op.drop_constraint('fk_reports_session_id_inspection_sessions', 'reports', type_='foreignkey')
    op.drop_index('ix_reports_session_id', table_name='reports')
    op.drop_column('reports', 'session_id')
    op.alter_column(
        'reports',
        'inspection_id',
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False
    )

    op.drop_constraint('fk_audit_chain_session_id_inspection_sessions', 'audit_chain', type_='foreignkey')
    op.drop_index('ix_audit_chain_session_id', table_name='audit_chain')
    op.drop_column('audit_chain', 'session_id')
