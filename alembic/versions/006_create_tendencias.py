"""Create tendencias table

Revision ID: 006
Revises: 005
Create Date: 2025-11-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMPTZ


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear tabla tendencias
    op.create_table(
        'tendencias',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()')),
        sa.Column('tema_id', UUID(as_uuid=True), nullable=False),
        sa.Column('fecha_hora', TIMESTAMPTZ, nullable=False),
        sa.Column('volumen_menciones', sa.INTEGER, nullable=False, server_default=sa.text('0')),
        sa.Column('tasa_crecimiento', sa.FLOAT, nullable=True),
        sa.Column('plataforma', sa.VARCHAR(50), nullable=False),
        sa.Column('ubicacion', sa.VARCHAR(100), nullable=True),
        sa.Column('edad_rango', sa.VARCHAR(20), nullable=True),
        sa.Column('genero', sa.VARCHAR(20), nullable=True),
        sa.Column('es_tendencia', sa.BOOLEAN, nullable=True, server_default=sa.text('false')),
        sa.Column('alerta_enviada', sa.BOOLEAN, nullable=True, server_default=sa.text('false')),
        sa.PrimaryKeyConstraint('fecha_hora', 'tema_id', 'plataforma', 'ubicacion', 'edad_rango', 'genero'),
    )

    # Agregar foreign key
    op.create_foreign_key(
        'fk_tendencias_tema',
        'tendencias',
        'temas_identificados',
        ['tema_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Agregar restricciones
    op.create_check_constraint(
        'tendencias_volumen_positive',
        'tendencias',
        'volumen_menciones >= 0'
    )

    # Crear índices
    op.create_index(
        'idx_tendencias_tema',
        'tendencias',
        ['tema_id', sa.text('fecha_hora DESC')]
    )
    op.create_index(
        'idx_tendencias_plataforma',
        'tendencias',
        ['plataforma', sa.text('fecha_hora DESC')]
    )
    op.execute(
        'CREATE INDEX idx_tendencias_es_tendencia ON tendencias (es_tendencia, fecha_hora DESC) '
        'WHERE es_tendencia = true'
    )
    op.execute(
        'CREATE INDEX idx_tendencias_alerta_pendiente ON tendencias (alerta_enviada, fecha_hora DESC) '
        'WHERE es_tendencia = true AND alerta_enviada = false'
    )


def downgrade() -> None:
    op.execute('DROP INDEX IF EXISTS idx_tendencias_alerta_pendiente')
    op.execute('DROP INDEX IF EXISTS idx_tendencias_es_tendencia')
    op.drop_index('idx_tendencias_plataforma', table_name='tendencias')
    op.drop_index('idx_tendencias_tema', table_name='tendencias')
    op.drop_constraint('tendencias_volumen_positive', 'tendencias', type_='check')
    op.drop_constraint('fk_tendencias_tema', 'tendencias', type_='foreignkey')
    op.drop_table('tendencias')
