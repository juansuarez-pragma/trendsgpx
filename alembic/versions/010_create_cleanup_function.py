"""Create cleanup_old_data function

Revision ID: 010
Revises: 009
Create Date: 2025-11-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear función PL/pgSQL para limpieza de datos antiguos
    op.execute("""
        CREATE OR REPLACE FUNCTION cleanup_old_data()
        RETURNS void AS $$
        BEGIN
            -- Eliminar contenido recolectado con más de 7 días
            DELETE FROM contenido_recolectado
            WHERE fecha_recoleccion < NOW() - INTERVAL '7 days';

            -- Eliminar temas huérfanos (ya no referenciados por contenido eliminado)
            DELETE FROM temas_identificados
            WHERE contenido_id NOT IN (SELECT id FROM contenido_recolectado);

            -- Eliminar demografía huérfana (ya no referenciada por temas eliminados)
            DELETE FROM demografia
            WHERE tema_id NOT IN (SELECT id FROM temas_identificados);

            -- Eliminar validaciones huérfanas con más de 7 días
            DELETE FROM validacion_tendencias
            WHERE tendencia_id IS NULL AND validado_at < NOW() - INTERVAL '7 days';

            RAISE NOTICE 'Old data cleanup completed';
        END;
        $$ LANGUAGE plpgsql;
    """)


def downgrade() -> None:
    # Eliminar función de limpieza
    op.execute('DROP FUNCTION IF EXISTS cleanup_old_data();')
