"""Initial schema - Enable extensions

Revision ID: 001
Revises:
Create Date: 2025-11-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Habilitar extensión TimescaleDB
    op.execute('CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;')

    # Habilitar extensión pg_trgm para búsqueda de texto
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')

    # Habilitar extensión uuid-ossp para generación de UUIDs
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')


def downgrade() -> None:
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp";')
    op.execute('DROP EXTENSION IF EXISTS pg_trgm;')
    op.execute('DROP EXTENSION IF EXISTS timescaledb CASCADE;')
