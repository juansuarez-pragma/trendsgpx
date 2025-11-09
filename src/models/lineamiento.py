"""
Modelo Lineamiento - Configuración para lineamientos de recolección de contenido
"""

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.models.base import Base


class Lineamiento(Base):
    """
    Modelo para lineamientos de recolección de contenido.

    Define qué palabras clave y plataformas se deben monitorear
    para recolectar contenido de redes sociales.
    """
    __tablename__ = "lineamientos"
    __table_args__ = (
        {"comment": "Configuración de lineamientos de recolección de contenido"}
    )

    # Campos principales
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único del lineamiento"
    )
    nombre = Column(
        String(255),
        unique=True,
        nullable=False,
        comment="Nombre único del lineamiento"
    )
    descripcion = Column(
        Text,
        comment="Descripción del propósito del lineamiento"
    )

    # Configuración de recolección
    keywords = Column(
        JSONB,
        nullable=False,
        comment="Array de palabras clave y hashtags a monitorear"
    )
    plataformas = Column(
        JSONB,
        nullable=False,
        comment="Array de plataformas a monitorear: youtube, reddit, mastodon"
    )

    # Estado
    activo = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Indica si el lineamiento está activo"
    )

    # Auditoría
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Fecha de creación del lineamiento"
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Fecha de última actualización"
    )
    created_by = Column(
        String(255),
        comment="Usuario que creó el lineamiento"
    )

    # Relaciones
    contenido_recolectado = relationship(
        "ContenidoRecolectado",
        back_populates="lineamiento",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __repr__(self):
        return f"<Lineamiento(id={self.id}, nombre='{self.nombre}', activo={self.activo})>"
