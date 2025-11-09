"""Create continuous aggregates for tendencias

Revision ID: 008
Revises: 007
Create Date: 2025-11-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear vista materializada de agregación por hora
    op.execute("""
        CREATE MATERIALIZED VIEW tendencias_por_hora
        WITH (timescaledb.continuous) AS
        SELECT
            time_bucket('1 hour', fecha_hora) AS hora,
            tema_id,
            plataforma,
            ubicacion,
            edad_rango,
            genero,
            SUM(volumen_menciones) AS total_menciones,
            AVG(tasa_crecimiento) AS tasa_crecimiento_promedio,
            COUNT(*) AS num_registros
        FROM tendencias
        GROUP BY hora, tema_id, plataforma, ubicacion, edad_rango, genero;
    """)

    # Agregar política de actualización continua para agregación horaria
    op.execute("""
        SELECT add_continuous_aggregate_policy(
            'tendencias_por_hora',
            start_offset => INTERVAL '3 hours',
            end_offset => INTERVAL '1 hour',
            schedule_interval => INTERVAL '1 hour',
            if_not_exists => TRUE
        );
    """)

    # Crear vista materializada de agregación por día
    op.execute("""
        CREATE MATERIALIZED VIEW tendencias_por_dia
        WITH (timescaledb.continuous) AS
        SELECT
            time_bucket('1 day', fecha_hora) AS dia,
            tema_id,
            plataforma,
            ubicacion,
            SUM(volumen_menciones) AS total_menciones,
            AVG(tasa_crecimiento) AS tasa_crecimiento_promedio,
            MAX(tasa_crecimiento) AS tasa_crecimiento_max
        FROM tendencias
        GROUP BY dia, tema_id, plataforma, ubicacion;
    """)

    # Agregar política de actualización continua para agregación diaria
    op.execute("""
        SELECT add_continuous_aggregate_policy(
            'tendencias_por_dia',
            start_offset => INTERVAL '3 days',
            end_offset => INTERVAL '1 day',
            schedule_interval => INTERVAL '1 day',
            if_not_exists => TRUE
        );
    """)


def downgrade() -> None:
    # Eliminar políticas de actualización continua
    op.execute("""
        SELECT remove_continuous_aggregate_policy('tendencias_por_dia', if_exists => TRUE);
    """)
    op.execute("""
        SELECT remove_continuous_aggregate_policy('tendencias_por_hora', if_exists => TRUE);
    """)

    # Eliminar vistas materializadas
    op.execute('DROP MATERIALIZED VIEW IF EXISTS tendencias_por_dia CASCADE;')
    op.execute('DROP MATERIALIZED VIEW IF EXISTS tendencias_por_hora CASCADE;')
