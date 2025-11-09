"""
Modelo Demografia - Segmentación demográfica de temas
"""

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.models.base import Base


class Demografia(Base):
    """
    Modelo para segmentación demográfica de temas.

    Almacena información demográfica inferida o directa sobre quién
    está discutiendo cada tema, organizada en jerarquía de 4 niveles:
    Plataforma -> Ubicación -> Edad -> Género
    """
    __tablename__ = "demografia"
    __table_args__ = (
        {"comment": "Segmentación demográfica de temas por jerarquía de 4 niveles"}
    )

    # Campos principales
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único del segmento demográfico"
    )
    tema_id = Column(
        UUID(as_uuid=True),
        ForeignKey("temas_identificados.id", ondelete="CASCADE"),
        nullable=False,
        comment="Referencia al tema identificado"
    )

    # Jerarquía de 4 niveles (FR-017)
    plataforma = Column(
        String(50),
        nullable=False,
        comment="Plataforma: youtube, reddit, mastodon"
    )
    ubicacion_pais = Column(
        String(100),
        comment="País de ubicación del segmento demográfico"
    )
    ubicacion_ciudad = Column(
        String(100),
        comment="Ciudad de ubicación del segmento demográfico"
    )
    edad_rango = Column(
        String(20),
        comment="Rango de edad: 18-24, 25-34, 35-44, 45-54, 55+, unknown"
    )
    genero = Column(
        String(20),
        comment="Género: male, female, other, unknown"
    )

    # Métricas
    conteo_menciones = Column(
        Integer,
        nullable=False,
        default=1,
        comment="Conteo de menciones del tema en este segmento"
    )
    confianza_score = Column(
        Float,
        comment="Nivel de confianza de la inferencia demográfica (0-1)"
    )

    # Método de inferencia
    metodo_inferencia = Column(
        String(50),
        comment="Método usado para inferir: direct, nlp, heuristic, ml_model"
    )

    # Metadatos
    calculado_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Fecha en que se calculó la demografía"
    )

    # Relación
    tema = relationship(
        "TemaIdentificado",
        back_populates="demografia"
    )

    def __repr__(self):
        return (
            f"<Demografia(id={self.id}, plataforma='{self.plataforma}', "
            f"ubicacion='{self.ubicacion_pais}/{self.ubicacion_ciudad}', "
            f"edad='{self.edad_rango}', genero='{self.genero}')>"
        )
