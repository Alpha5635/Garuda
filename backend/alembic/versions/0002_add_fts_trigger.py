"""Add PostgreSQL Full-Text Search (FTS) automatic trigger on inspections.

Revision ID: 0002_add_fts_trigger
Revises: 0001_initial_labelsetu_schema
Create Date: 2026-08-22 14:40:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0002_add_fts_trigger'
down_revision: Union[str, None] = '0001_initial_labelsetu_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    if is_postgres:
        # 1. Create or replace PL/pgSQL trigger function incorporating:
        #    - Brand canonical name (Weight A)
        #    - Product generic name (Weight A)
        #    - District and State code (Weight B)
        #    - Channel, Status, SKU (Weight C)
        #    - Officer notes (Weight D)
        op.execute("""
        CREATE OR REPLACE FUNCTION inspections_search_vector_trigger() RETURNS trigger AS $$
        DECLARE
            v_brand_name text := '';
            v_generic_name text := '';
            v_sku text := '';
        BEGIN
            IF NEW.product_id IS NOT NULL THEN
                SELECT COALESCE(b.canonical_name, ''), COALESCE(p.generic_name, ''), COALESCE(p.sku, '')
                INTO v_brand_name, v_generic_name, v_sku
                FROM products p
                LEFT JOIN brands b ON p.brand_id = b.id
                WHERE p.id = NEW.product_id;
            END IF;

            NEW.search_vector :=
                setweight(to_tsvector('english', coalesce(v_brand_name, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(v_generic_name, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(NEW.district, '')), 'B') ||
                setweight(to_tsvector('english', coalesce(NEW.state_code, '')), 'B') ||
                setweight(to_tsvector('english', coalesce(NEW.channel, '')), 'C') ||
                setweight(to_tsvector('english', coalesce(NEW.status, '')), 'C') ||
                setweight(to_tsvector('english', coalesce(v_sku, '')), 'C') ||
                setweight(to_tsvector('english', coalesce(NEW.officer_notes, '')), 'D');

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """)

        # 2. Attach BEFORE INSERT OR UPDATE trigger on inspections
        op.execute("""
        DROP TRIGGER IF EXISTS trg_inspections_search_vector ON inspections;
        CREATE TRIGGER trg_inspections_search_vector
        BEFORE INSERT OR UPDATE ON inspections
        FOR EACH ROW
        EXECUTE FUNCTION inspections_search_vector_trigger();
        """)

        # 3. Backfill search vectors for existing inspections
        op.execute("""
        UPDATE inspections SET updated_at = CURRENT_TIMESTAMP WHERE search_vector IS NULL;
        """)


def downgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    if is_postgres:
        op.execute("DROP TRIGGER IF EXISTS trg_inspections_search_vector ON inspections;")
        op.execute("DROP FUNCTION IF EXISTS inspections_search_vector_trigger();")
