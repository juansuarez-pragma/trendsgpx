"""Create lineamientos table

Revision ID: 002
Revises: 001
Create Date: 2025-11-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMPTZ


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear tabla lineamientos
    op.create_table(
        'lineamientos',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('nombre', sa.VARCHAR(255), nullable=False),
        sa.Column('descripcion', sa.TEXT, nullable=True),
        sa.Column('keywords', JSONB, nullable=False),
        sa.Column('plataformas', JSONB, nullable=False),
        sa.Column('activo', sa.BOOLEAN, nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', TIMESTAMPTZ, nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', TIMESTAMPTZ, nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_by', sa.VARCHAR(255), nullable=True),
    )

    # Agregar restricciones
    op.create_unique_constraint('lineamiento_nombre_unique', 'lineamientos', ['nombre'])
    op.create_check_constraint(
        'lineamiento_keywords_not_empty',
        'lineamientos',
        'jsonb_array_length(keywords) > 0'
    )
    op.create_check_constraint(
        'lineamiento_plataformas_not_empty',
        'lineamientos',
        'jsonb_array_length(plataformas) > 0'
    )

    # Crear índices
    op.execute(
        'CREATE INDEX idx_lineamientos_activo ON lineamientos (activo) WHERE activo = true'
    )
    op.create_index(
        'idx_lineamientos_keywords',
        'lineamientos',
        ['keywords'],
        postgresql_using='gin'
    )


def downgrade() -> None:
    op.drop_index('idx_lineamientos_keywords', table_name='lineamientos')
    op.execute('DROP INDEX IF EXISTS idx_lineamientos_activo')
    op.drop_constraint('lineamiento_plataformas_not_empty', 'lineamientos', type_='check')
    op.drop_constraint('lineamiento_keywords_not_empty', 'lineamientos', type_='check')
    op.drop_constraint('lineamiento_nombre_unique', 'lineamientos', type_='unique')
    op.drop_table('lineamientos')
