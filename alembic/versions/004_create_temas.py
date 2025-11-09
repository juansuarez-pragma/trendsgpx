"""Create temas_identificados table

Revision ID: 004
Revises: 003
Create Date: 2025-11-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMPTZ, ARRAY


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear tabla temas_identificados
    op.create_table(
        'temas_identificados',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('contenido_id', UUID(as_uuid=True), nullable=False),
        sa.Column('tema_nombre', sa.VARCHAR(255), nullable=False),
        sa.Column('relevancia_score', sa.FLOAT, nullable=False),
        sa.Column('keywords', ARRAY(sa.TEXT), nullable=True),
        sa.Column('sentimiento', sa.VARCHAR(20), nullable=True),
        sa.Column('sentimiento_score', sa.FLOAT, nullable=True),
        sa.Column('entidades_mencionadas', JSONB, nullable=True),
        sa.Column('modelo_version', sa.VARCHAR(50), nullable=True),
        sa.Column('identificado_at', TIMESTAMPTZ, nullable=False, server_default=sa.text('NOW()')),
    )

    # Agregar foreign key
    op.create_foreign_key(
        'fk_temas_contenido',
        'temas_identificados',
        'contenido_recolectado',
        ['contenido_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Agregar restricciones
    op.create_check_constraint(
        'tema_relevancia_valid',
        'temas_identificados',
        'relevancia_score BETWEEN 0 AND 1'
    )
    op.create_check_constraint(
        'tema_sentimiento_score_valid',
        'temas_identificados',
        'sentimiento_score BETWEEN -1 AND 1'
    )
    op.create_check_constraint(
        'tema_sentimiento_valid',
        'temas_identificados',
        "sentimiento IN ('positive', 'negative', 'neutral', 'mixed')"
    )

    # Crear índices
    op.create_index('idx_temas_contenido', 'temas_identificados', ['contenido_id'])
    op.create_index('idx_temas_nombre', 'temas_identificados', ['tema_nombre'])
    op.create_index(
        'idx_temas_relevancia',
        'temas_identificados',
        [sa.text('relevancia_score DESC')]
    )
    op.create_index(
        'idx_temas_fecha',
        'temas_identificados',
        [sa.text('identificado_at DESC')]
    )
    op.create_index(
        'idx_temas_keywords',
        'temas_identificados',
        ['keywords'],
        postgresql_using='gin'
    )


def downgrade() -> None:
    op.drop_index('idx_temas_keywords', table_name='temas_identificados')
    op.drop_index('idx_temas_fecha', table_name='temas_identificados')
    op.drop_index('idx_temas_relevancia', table_name='temas_identificados')
    op.drop_index('idx_temas_nombre', table_name='temas_identificados')
    op.drop_index('idx_temas_contenido', table_name='temas_identificados')
    op.drop_constraint('tema_sentimiento_valid', 'temas_identificados', type_='check')
    op.drop_constraint('tema_sentimiento_score_valid', 'temas_identificados', type_='check')
    op.drop_constraint('tema_relevancia_valid', 'temas_identificados', type_='check')
    op.drop_constraint('fk_temas_contenido', 'temas_identificados', type_='foreignkey')
    op.drop_table('temas_identificados')
