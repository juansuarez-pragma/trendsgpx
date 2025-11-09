"""Convert tendencias to TimescaleDB hypertable

Revision ID: 007
Revises: 006
Create Date: 2025-11-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Convertir tabla tendencias a hipertabla de TimescaleDB
    op.execute("""
        SELECT create_hypertable(
            'tendencias',
            'fecha_hora',
            chunk_time_interval => INTERVAL '7 days',
            if_not_exists => TRUE
        );
    """)

    # Agregar política de retención de 7 días
    op.execute("""
        SELECT add_retention_policy(
            'tendencias',
            INTERVAL '7 days',
            if_not_exists => TRUE
        );
    """)


def downgrade() -> None:
    # Eliminar política de retención
    op.execute("""
        SELECT remove_retention_policy('tendencias', if_exists => TRUE);
    """)

    # Nota: TimescaleDB no permite convertir una hipertabla de vuelta a tabla normal fácilmente
    # Se requeriría recrear la tabla sin TimescaleDB, lo cual perdería datos
    # Para propósitos de downgrade, solo removemos las políticas
    pass
