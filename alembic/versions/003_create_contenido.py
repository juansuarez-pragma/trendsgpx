"""Create contenido_recolectado table

Revision ID: 003
Revises: 002
Create Date: 2025-11-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMPTZ


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear tabla contenido_recolectado
    op.create_table(
        'contenido_recolectado',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('lineamiento_id', UUID(as_uuid=True), nullable=False),
        sa.Column('plataforma', sa.VARCHAR(50), nullable=False),
        sa.Column('plataforma_id', sa.VARCHAR(255), nullable=False),
        sa.Column('contenido_texto', sa.TEXT, nullable=False),
        sa.Column('titulo', sa.VARCHAR(500), nullable=True),
        sa.Column('autor', sa.VARCHAR(255), nullable=True),
        sa.Column('url', sa.TEXT, nullable=True),
        sa.Column('metadata', JSONB, nullable=True),
        sa.Column('fecha_publicacion', TIMESTAMPTZ, nullable=False),
        sa.Column('fecha_recoleccion', TIMESTAMPTZ, nullable=False, server_default=sa.text('NOW()')),
        sa.Column('idioma', sa.VARCHAR(10), nullable=True, server_default=sa.text("'es'")),
        sa.Column('nlp_procesado', sa.BOOLEAN, nullable=True, server_default=sa.text('false')),
        sa.Column('nlp_procesado_at', TIMESTAMPTZ, nullable=True),
    )

    # Agregar foreign key
    op.create_foreign_key(
        'fk_contenido_lineamiento',
        'contenido_recolectado',
        'lineamientos',
        ['lineamiento_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Agregar restricciones
    op.create_unique_constraint(
        'contenido_plataforma_id_unique',
        'contenido_recolectado',
        ['plataforma', 'plataforma_id']
    )
    op.create_check_constraint(
        'contenido_plataforma_valid',
        'contenido_recolectado',
        "plataforma IN ('youtube', 'reddit', 'mastodon')"
    )
    op.create_check_constraint(
        'contenido_texto_not_empty',
        'contenido_recolectado',
        'length(contenido_texto) > 0'
    )

    # Crear índices
    op.create_index('idx_contenido_lineamiento', 'contenido_recolectado', ['lineamiento_id'])
    op.create_index('idx_contenido_plataforma', 'contenido_recolectado', ['plataforma'])
    op.create_index(
        'idx_contenido_fecha_publicacion',
        'contenido_recolectado',
        [sa.text('fecha_publicacion DESC')]
    )
    op.create_index(
        'idx_contenido_fecha_recoleccion',
        'contenido_recolectado',
        [sa.text('fecha_recoleccion DESC')]
    )
    op.execute(
        'CREATE INDEX idx_contenido_nlp_pending ON contenido_recolectado (nlp_procesado) '
        'WHERE nlp_procesado = false'
    )
    op.execute(
        "CREATE INDEX idx_contenido_texto_search ON contenido_recolectado "
        "USING GIN (to_tsvector('spanish', contenido_texto))"
    )


def downgrade() -> None:
    op.execute('DROP INDEX IF EXISTS idx_contenido_texto_search')
    op.execute('DROP INDEX IF EXISTS idx_contenido_nlp_pending')
    op.drop_index('idx_contenido_fecha_recoleccion', table_name='contenido_recolectado')
    op.drop_index('idx_contenido_fecha_publicacion', table_name='contenido_recolectado')
    op.drop_index('idx_contenido_plataforma', table_name='contenido_recolectado')
    op.drop_index('idx_contenido_lineamiento', table_name='contenido_recolectado')
    op.drop_constraint('contenido_texto_not_empty', 'contenido_recolectado', type_='check')
    op.drop_constraint('contenido_plataforma_valid', 'contenido_recolectado', type_='check')
    op.drop_constraint('contenido_plataforma_id_unique', 'contenido_recolectado', type_='unique')
    op.drop_constraint('fk_contenido_lineamiento', 'contenido_recolectado', type_='foreignkey')
    op.drop_table('contenido_recolectado')
