"""
Schemas Pydantic para Lineamientos
"""

from pydantic import BaseModel, Field, field_validator
from typing import List
from uuid import UUID
from datetime import datetime


class LineamientoBase(BaseModel):
    """Schema base con campos comunes"""
    nombre: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nombre único del lineamiento",
        examples=["Tecnología 2025"],
    )
    keywords: List[str] = Field(
        ...,
        min_length=1,
        description="Lista de keywords para búsqueda",
        examples=[["IA", "inteligencia artificial", "machine learning"]],
    )
    plataformas: List[str] = Field(
        ...,
        min_length=1,
        description="Plataformas donde buscar (youtube, reddit, mastodon)",
        examples=[["youtube", "reddit"]],
    )

    @field_validator("keywords")
    @classmethod
    def validate_keywords(cls, v: List[str]) -> List[str]:
        """Valida que keywords no esté vacío y no contenga strings vacíos"""
        if not v:
            raise ValueError("keywords no puede estar vacío")

        # Limpiar whitespace y filtrar vacíos
        cleaned = [kw.strip() for kw in v if kw.strip()]

        if not cleaned:
            raise ValueError("keywords debe contener al menos una keyword válida")

        return cleaned

    @field_validator("plataformas")
    @classmethod
    def validate_plataformas(cls, v: List[str]) -> List[str]:
        """Valida que plataformas sean válidas"""
        if not v:
            raise ValueError("plataformas no puede estar vacío")

        valid_platforms = {"youtube", "reddit", "mastodon"}

        # Normalizar a lowercase
        normalized = [p.lower().strip() for p in v]

        # Validar que todas sean plataformas válidas
        invalid = set(normalized) - valid_platforms
        if invalid:
            raise ValueError(
                f"Plataformas inválidas: {invalid}. "
                f"Plataformas válidas: {valid_platforms}"
            )

        # Eliminar duplicados
        return list(set(normalized))


class LineamientoCreate(LineamientoBase):
    """
    Schema para crear un nuevo lineamiento.

    Ejemplo:
    ```json
    {
        "nombre": "Tecnología 2025",
        "keywords": ["IA", "inteligencia artificial", "GPT", "transformers"],
        "plataformas": ["youtube", "reddit"]
    }
    ```
    """
    pass


class LineamientoUpdate(BaseModel):
    """
    Schema para actualizar un lineamiento existente.
    Todos los campos son opcionales.

    Ejemplo:
    ```json
    {
        "keywords": ["IA", "machine learning", "deep learning"],
        "activo": false
    }
    ```
    """
    nombre: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Nuevo nombre del lineamiento",
    )
    keywords: List[str] | None = Field(
        None,
        min_length=1,
        description="Nueva lista de keywords",
    )
    plataformas: List[str] | None = Field(
        None,
        min_length=1,
        description="Nueva lista de plataformas",
    )
    activo: bool | None = Field(
        None,
        description="Estado activo/inactivo del lineamiento",
    )

    @field_validator("keywords")
    @classmethod
    def validate_keywords(cls, v: List[str] | None) -> List[str] | None:
        """Valida keywords si está presente"""
        if v is None:
            return v

        if not v:
            raise ValueError("keywords no puede estar vacío")

        cleaned = [kw.strip() for kw in v if kw.strip()]

        if not cleaned:
            raise ValueError("keywords debe contener al menos una keyword válida")

        return cleaned

    @field_validator("plataformas")
    @classmethod
    def validate_plataformas(cls, v: List[str] | None) -> List[str] | None:
        """Valida plataformas si está presente"""
        if v is None:
            return v

        if not v:
            raise ValueError("plataformas no puede estar vacío")

        valid_platforms = {"youtube", "reddit", "mastodon"}
        normalized = [p.lower().strip() for p in v]

        invalid = set(normalized) - valid_platforms
        if invalid:
            raise ValueError(
                f"Plataformas inválidas: {invalid}. "
                f"Plataformas válidas: {valid_platforms}"
            )

        return list(set(normalized))


class LineamientoResponse(LineamientoBase):
    """
    Schema para respuesta de un lineamiento.
    Incluye todos los campos del modelo.

    Ejemplo:
    ```json
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "nombre": "Tecnología 2025",
        "keywords": ["IA", "inteligencia artificial"],
        "plataformas": ["youtube", "reddit"],
        "activo": true,
        "created_at": "2025-01-15T10:30:00Z",
        "updated_at": "2025-01-15T10:30:00Z"
    }
    ```
    """
    id: UUID = Field(
        ...,
        description="ID único del lineamiento (UUID)",
    )
    activo: bool = Field(
        ...,
        description="Indica si el lineamiento está activo",
    )
    created_at: datetime = Field(
        ...,
        description="Fecha de creación",
    )
    updated_at: datetime = Field(
        ...,
        description="Fecha de última actualización",
    )

    class Config:
        """Configuración de Pydantic"""
        from_attributes = True  # Permite crear desde ORM models


class LineamientoListResponse(BaseModel):
    """
    Schema para respuesta de lista de lineamientos.

    Ejemplo:
    ```json
    {
        "total": 10,
        "items": [...]
    }
    ```
    """
    total: int = Field(
        ...,
        ge=0,
        description="Número total de lineamientos",
    )
    items: List[LineamientoResponse] = Field(
        ...,
        description="Lista de lineamientos",
    )
