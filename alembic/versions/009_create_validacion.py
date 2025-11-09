"""Create validacion_tendencias table

Revision ID: 009
Revises: 008
Create Date: 2025-11-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMPTZ


# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear tabla validacion_tendencias
    op.create_table(
        'validacion_tendencias',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tendencia_id', UUID(as_uuid=True), nullable=True),
        sa.Column('tema_nombre', sa.VARCHAR(255), nullable=False),
        sa.Column('fuente_validacion', sa.VARCHAR(50), nullable=False, server_default=sa.text("'google_trends'")),
        sa.Column('google_trends_data', JSONB, nullable=True),
        sa.Column('indice_coincidencia', sa.FLOAT, nullable=True),
        sa.Column('validada', sa.BOOLEAN, nullable=False),
        sa.Column('en_google_trends', sa.BOOLEAN, nullable=True),
        sa.Column('solo_en_plataforma', sa.BOOLEAN, nullable=True),
        sa.Column('validado_at', TIMESTAMPTZ, nullable=False, server_default=sa.text('NOW()')),
    )

    # Agregar foreign key con ON DELETE SET NULL
    op.create_foreign_key(
        'fk_validacion_tendencia',
        'validacion_tendencias',
        'tendencias',
        ['tendencia_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # Agregar restricciones
    op.create_check_constraint(
        'validacion_indice_valid',
        'validacion_tendencias',
        'indice_coincidencia BETWEEN 0 AND 1'
    )
    op.create_check_constraint(
        'validacion_fuente_valid',
        'validacion_tendencias',
        "fuente_validacion IN ('google_trends', 'manual', 'other')"
    )

    # Crear índices
    op.create_index('idx_validacion_tendencia', 'validacion_tendencias', ['tendencia_id'])
    op.create_index('idx_validacion_validada', 'validacion_tendencias', ['validada'])
    op.create_index(
        'idx_validacion_fecha',
        'validacion_tendencias',
        [sa.text('validado_at DESC')]
    )
    op.execute(
        'CREATE INDEX idx_validacion_gap ON validacion_tendencias (solo_en_plataforma) '
        'WHERE solo_en_plataforma = true'
    )


def downgrade() -> None:
    op.execute('DROP INDEX IF EXISTS idx_validacion_gap')
    op.drop_index('idx_validacion_fecha', table_name='validacion_tendencias')
    op.drop_index('idx_validacion_validada', table_name='validacion_tendencias')
    op.drop_index('idx_validacion_tendencia', table_name='validacion_tendencias')
    op.drop_constraint('validacion_fuente_valid', 'validacion_tendencias', type_='check')
    op.drop_constraint('validacion_indice_valid', 'validacion_tendencias', type_='check')
    op.drop_constraint('fk_validacion_tendencia', 'validacion_tendencias', type_='foreignkey')
    op.drop_table('validacion_tendencias')
