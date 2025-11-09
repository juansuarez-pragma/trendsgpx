"""
Modelo TemaIdentificado - Temas extraídos mediante NLP
"""

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, Text, ForeignKey, ARRAY, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.models.base import Base


class TemaIdentificado(Base):
    """
    Modelo para temas identificados mediante procesamiento NLP.

    Almacena temas extraídos del contenido usando BERTopic,
    junto con análisis de sentimiento y entidades nombradas.
    """
    __tablename__ = "temas_identificados"
    __table_args__ = (
        {"comment": "Temas extraídos del contenido mediante NLP"}
    )

    # Campos principales
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único del tema"
    )
    contenido_id = Column(
        UUID(as_uuid=True),
        ForeignKey("contenido_recolectado.id", ondelete="CASCADE"),
        nullable=False,
        comment="Referencia al contenido del cual se extrajo el tema"
    )

    # Información del tema
    tema_nombre = Column(
        String(255),
        nullable=False,
        comment="Nombre descriptivo del tema identificado"
    )
    relevancia_score = Column(
        Float,
        nullable=False,
        comment="Puntuación de relevancia del tema (0-1)"
    )
    keywords = Column(
        ARRAY(Text),
        comment="Array de palabras clave asociadas con el tema"
    )

    # Análisis de sentimiento
    sentimiento = Column(
        String(20),
        comment="Sentimiento del tema: positive, negative, neutral, mixed"
    )
    sentimiento_score = Column(
        Float,
        comment="Puntuación de sentimiento (-1 a 1)"
    )

    # Entidades nombradas
    entidades_mencionadas = Column(
        JSONB,
        comment="Entidades nombradas: persons, organizations, locations"
    )

    # Metadatos
    modelo_version = Column(
        String(50),
        comment="Versión del modelo NLP utilizado (ej: BERTopic-0.16.0)"
    )
    identificado_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Fecha en que se identificó el tema"
    )

    # Relaciones
    contenido = relationship(
        "ContenidoRecolectado",
        back_populates="temas"
    )
    demografia = relationship(
        "Demografia",
        back_populates="tema",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    tendencias = relationship(
        "Tendencia",
        back_populates="tema",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __repr__(self):
        return (
            f"<TemaIdentificado(id={self.id}, tema_nombre='{self.tema_nombre}', "
            f"relevancia={self.relevancia_score:.2f})>"
        )
