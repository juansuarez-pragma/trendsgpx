"""
Modelo Tendencia - Datos de series temporales para temas en tendencia
"""

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, Text, ForeignKey, PrimaryKeyConstraint, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.models.base import Base


class Tendencia(Base):
    """
    Modelo para tendencias de temas en series temporales.

    Almacena instantáneas horarias de métricas de tendencias,
    optimizado para TimescaleDB con clave primaria compuesta.
    Incluye segmentación demográfica para análisis jerárquico.
    """
    __tablename__ = "tendencias"
    __table_args__ = (
        PrimaryKeyConstraint(
            "fecha_hora",
            "tema_id",
            "plataforma",
            "ubicacion",
            "edad_rango",
            "genero",
            name="pk_tendencias"
        ),
        {"comment": "Datos de series temporales para temas en tendencia (hipertabla TimescaleDB)"}
    )

    # ID generado pero no es primary key
    id = Column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        comment="Identificador único de la tendencia"
    )
    tema_id = Column(
        UUID(as_uuid=True),
        ForeignKey("temas_identificados.id", ondelete="CASCADE"),
        nullable=False,
        comment="Referencia al tema identificado"
    )

    # Series temporales
    fecha_hora = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Marca de tiempo de la instantánea"
    )

    # Métricas
    volumen_menciones = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Volumen de menciones en este período"
    )
    tasa_crecimiento = Column(
        Float,
        comment="Tasa de crecimiento comparada con período anterior"
    )

    # Segmentación (para API jerárquica FR-017)
    plataforma = Column(
        String(50),
        nullable=False,
        comment="Plataforma: youtube, reddit, mastodon"
    )
    ubicacion = Column(
        String(100),
        nullable=False,
        comment="Ubicación geográfica del segmento"
    )
    edad_rango = Column(
        String(20),
        nullable=False,
        comment="Rango de edad del segmento"
    )
    genero = Column(
        String(20),
        nullable=False,
        comment="Género del segmento"
    )

    # Estado de tendencia
    es_tendencia = Column(
        Boolean,
        default=False,
        comment="Indica si está marcado como tendencia activa"
    )
    alerta_enviada = Column(
        Boolean,
        default=False,
        comment="Indica si se envió alerta para esta tendencia"
    )

    # Relaciones
    tema = relationship(
        "TemaIdentificado",
        back_populates="tendencias"
    )
    validacion = relationship(
        "ValidacionTendencia",
        back_populates="tendencia",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __repr__(self):
        return (
            f"<Tendencia(tema_id={self.tema_id}, fecha_hora={self.fecha_hora}, "
            f"volumen={self.volumen_menciones}, crecimiento={self.tasa_crecimiento:.2f if self.tasa_crecimiento else 0})>"
        )
