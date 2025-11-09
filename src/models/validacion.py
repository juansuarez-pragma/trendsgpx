"""
Modelo ValidacionTendencia - Validación de tendencias con fuentes externas
"""

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.models.base import Base


class ValidacionTendencia(Base):
    """
    Modelo para validación de tendencias detectadas.

    Valida tendencias detectadas en las plataformas mediante
    validación cruzada con Google Trends y otras fuentes externas.
    Permite identificar tendencias exclusivas de plataforma (gap analysis).
    """
    __tablename__ = "validacion_tendencias"
    __table_args__ = (
        {"comment": "Validación de tendencias con fuentes externas (Google Trends)"}
    )

    # Campos principales
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único de la validación"
    )
    tendencia_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tendencias.id", ondelete="SET NULL"),
        nullable=True,
        comment="Referencia a la tendencia validada (nullable para auditoría)"
    )
    tema_nombre = Column(
        String(255),
        nullable=False,
        comment="Nombre del tema validado"
    )

    # Fuente de validación
    fuente_validacion = Column(
        String(50),
        nullable=False,
        default="google_trends",
        comment="Fuente de validación: google_trends, manual, other"
    )

    # Datos de Google Trends
    google_trends_data = Column(
        JSONB,
        comment="Respuesta cruda de Google Trends API"
    )

    # Resultados de validación
    indice_coincidencia = Column(
        Float,
        comment="Índice de coincidencia con la fuente externa (0-1)"
    )
    validada = Column(
        Boolean,
        nullable=False,
        comment="Indica si la tendencia fue validada exitosamente"
    )

    # Análisis de brechas (FR-022)
    en_google_trends = Column(
        Boolean,
        comment="Indica si la tendencia también aparece en Google Trends"
    )
    solo_en_plataforma = Column(
        Boolean,
        comment="Indica si es tendencia exclusiva de plataforma (gap analysis)"
    )

    # Metadatos
    validado_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Fecha en que se realizó la validación"
    )

    # Relación
    tendencia = relationship(
        "Tendencia",
        back_populates="validacion"
    )

    def __repr__(self):
        return (
            f"<ValidacionTendencia(id={self.id}, tema='{self.tema_nombre}', "
            f"validada={self.validada}, solo_plataforma={self.solo_en_plataforma})>"
        )
