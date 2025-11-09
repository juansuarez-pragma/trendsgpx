"""
Modelo ContenidoRecolectado - Contenido crudo recolectado de plataformas
"""

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.models.base import Base


class ContenidoRecolectado(Base):
    """
    Modelo para contenido recolectado de redes sociales.

    Almacena el contenido crudo obtenido de YouTube, Reddit y Mastodon,
    junto con metadatos de engagement y estado de procesamiento NLP.
    """
    __tablename__ = "contenido_recolectado"
    __table_args__ = (
        {"comment": "Contenido crudo recolectado de plataformas de redes sociales"}
    )

    # Campos principales
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único del contenido"
    )
    lineamiento_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lineamientos.id", ondelete="CASCADE"),
        nullable=False,
        comment="Referencia al lineamiento que recolectó este contenido"
    )

    # Datos de plataforma
    plataforma = Column(
        String(50),
        nullable=False,
        comment="Plataforma de origen: youtube, reddit, mastodon"
    )
    plataforma_id = Column(
        String(255),
        nullable=False,
        comment="ID único del contenido en la plataforma"
    )

    # Contenido
    contenido_texto = Column(
        Text,
        nullable=False,
        comment="Texto del contenido recolectado"
    )
    titulo = Column(
        String(500),
        comment="Título del contenido"
    )
    autor = Column(
        String(255),
        comment="Autor o creador del contenido"
    )
    url = Column(
        Text,
        comment="URL del contenido original"
    )

    # Métricas de engagement
    metadata = Column(
        JSONB,
        comment="Metadatos de engagement: likes, shares, comments, views, etc."
    )

    # Marcas de tiempo
    fecha_publicacion = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha en que fue publicado el contenido"
    )
    fecha_recoleccion = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Fecha en que fue recolectado el contenido"
    )

    # Detección de idioma
    idioma = Column(
        String(10),
        default="es",
        comment="Código ISO 639-1 del idioma"
    )

    # Estado de procesamiento NLP
    nlp_procesado = Column(
        Boolean,
        default=False,
        comment="Indica si el contenido ha sido procesado por NLP"
    )
    nlp_procesado_at = Column(
        DateTime(timezone=True),
        comment="Fecha en que se procesó el contenido con NLP"
    )

    # Relaciones
    lineamiento = relationship(
        "Lineamiento",
        back_populates="contenido_recolectado"
    )
    temas = relationship(
        "TemaIdentificado",
        back_populates="contenido",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __repr__(self):
        return (
            f"<ContenidoRecolectado(id={self.id}, plataforma='{self.plataforma}', "
            f"titulo='{self.titulo[:30] if self.titulo else None}...')>"
        )
