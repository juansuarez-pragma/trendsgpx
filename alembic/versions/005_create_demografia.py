"""Create demografia table

Revision ID: 005
Revises: 004
Create Date: 2025-11-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMPTZ


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear tabla demografia
    op.create_table(
        'demografia',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tema_id', UUID(as_uuid=True), nullable=False),
        sa.Column('plataforma', sa.VARCHAR(50), nullable=False),
        sa.Column('ubicacion_pais', sa.VARCHAR(100), nullable=True),
        sa.Column('ubicacion_ciudad', sa.VARCHAR(100), nullable=True),
        sa.Column('edad_rango', sa.VARCHAR(20), nullable=True),
        sa.Column('genero', sa.VARCHAR(20), nullable=True),
        sa.Column('conteo_menciones', sa.INTEGER, nullable=False, server_default=sa.text('1')),
        sa.Column('confianza_score', sa.FLOAT, nullable=True),
        sa.Column('metodo_inferencia', sa.VARCHAR(50), nullable=True),
        sa.Column('calculado_at', TIMESTAMPTZ, nullable=False, server_default=sa.text('NOW()')),
    )

    # Agregar foreign key
    op.create_foreign_key(
        'fk_demografia_tema',
        'demografia',
        'temas_identificados',
        ['tema_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Agregar restricciones
    op.create_check_constraint(
        'demografia_plataforma_valid',
        'demografia',
        "plataforma IN ('youtube', 'reddit', 'mastodon')"
    )
    op.create_check_constraint(
        'demografia_edad_valid',
        'demografia',
        "edad_rango IN ('18-24', '25-34', '35-44', '45-54', '55+', 'unknown')"
    )
    op.create_check_constraint(
        'demografia_genero_valid',
        'demografia',
        "genero IN ('male', 'female', 'other', 'unknown')"
    )
    op.create_check_constraint(
        'demografia_confianza_valid',
        'demografia',
        'confianza_score BETWEEN 0 AND 1'
    )
    op.create_unique_constraint(
        'demografia_unique_segment',
        'demografia',
        ['tema_id', 'plataforma', 'ubicacion_pais', 'ubicacion_ciudad', 'edad_rango', 'genero']
    )

    # Crear índices
    op.create_index('idx_demografia_tema', 'demografia', ['tema_id'])
    op.create_index('idx_demografia_plataforma', 'demografia', ['plataforma'])
    op.create_index('idx_demografia_ubicacion', 'demografia', ['ubicacion_pais', 'ubicacion_ciudad'])
    op.create_index('idx_demografia_edad', 'demografia', ['edad_rango'])
    op.create_index('idx_demografia_genero', 'demografia', ['genero'])
    op.create_index(
        'idx_demografia_confianza',
        'demografia',
        [sa.text('confianza_score DESC')]
    )
    op.create_index(
        'idx_demografia_hierarchy',
        'demografia',
        ['plataforma', 'ubicacion_pais', 'edad_rango', 'genero']
    )


def downgrade() -> None:
    op.drop_index('idx_demografia_hierarchy', table_name='demografia')
    op.drop_index('idx_demografia_confianza', table_name='demografia')
    op.drop_index('idx_demografia_genero', table_name='demografia')
    op.drop_index('idx_demografia_edad', table_name='demografia')
    op.drop_index('idx_demografia_ubicacion', table_name='demografia')
    op.drop_index('idx_demografia_plataforma', table_name='demografia')
    op.drop_index('idx_demografia_tema', table_name='demografia')
    op.drop_constraint('demografia_unique_segment', 'demografia', type_='unique')
    op.drop_constraint('demografia_confianza_valid', 'demografia', type_='check')
    op.drop_constraint('demografia_genero_valid', 'demografia', type_='check')
    op.drop_constraint('demografia_edad_valid', 'demografia', type_='check')
    op.drop_constraint('demografia_plataforma_valid', 'demografia', type_='check')
    op.drop_constraint('fk_demografia_tema', 'demografia', type_='foreignkey')
    op.drop_table('demografia')
